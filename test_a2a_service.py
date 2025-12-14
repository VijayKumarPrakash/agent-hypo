#!/usr/bin/env python3
"""Test script for A2A service.

This script tests the White Agent A2A service locally or remotely.
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"  # Change this for remote testing

# Example public URLs for testing (you can replace with your own)
EXAMPLE_CONTEXT_URL = "https://raw.githubusercontent.com/example/data/context.txt"
EXAMPLE_DATA_URL = "https://raw.githubusercontent.com/example/data/experiment.csv"


def test_health_check():
    """Test the /health endpoint."""
    print("\n=== Testing /health endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        response.raise_for_status()
        data = response.json()

        print("✓ Health check successful")
        print(f"  Status: {data['status']}")
        print(f"  Version: {data['version']}")
        print(f"  LLM Available: {data['llm_available']}")
        print(f"  Storage Configured: {data['storage_configured']}")

        return data['storage_configured']

    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_root_endpoint():
    """Test the root / endpoint."""
    print("\n=== Testing / endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        response.raise_for_status()
        data = response.json()

        print("✓ Root endpoint successful")
        print(f"  Service: {data['service']}")
        print(f"  Version: {data['version']}")
        print(f"  Status: {data['status']}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ Root endpoint failed: {e}")
        return False


def test_run_analysis(context_url: str, data_url: str, mode: str = "auto"):
    """Test the /run endpoint with provided URLs."""
    print(f"\n=== Testing /run endpoint (mode: {mode}) ===")
    print(f"Context URL: {context_url}")
    print(f"Data URL: {data_url}")

    payload = {
        "context_url": context_url,
        "data_url": data_url,
        "mode": mode
    }

    try:
        print("\nSending request...")
        start_time = time.time()

        response = requests.post(
            f"{BASE_URL}/run",
            json=payload,
            timeout=120  # Allow up to 2 minutes for analysis
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            print(f"✓ Analysis successful (took {elapsed:.1f}s)")
            print(f"\n  Run ID: {data['run_id']}")
            print(f"  Status: {data['status']}")
            print(f"  Mode Used: {data['mode_used']}")
            print(f"  Analysis Type: {data.get('analysis_type', 'N/A')}")
            print(f"  Experiment Type: {data.get('experiment_type', 'N/A')}")

            print("\n  Analysis Summary:")
            summary = data['analysis_summary']
            print(f"    Sample Size: {summary['sample_size']}")
            print(f"    Treatment Effect: {summary.get('treatment_effect', 'N/A')}")
            print(f"    P-value: {summary.get('p_value', 'N/A')}")
            print(f"    Significant: {summary.get('statistically_significant', 'N/A')}")

            print("\n  Output URLs:")
            outputs = data['outputs']
            print(f"    Report: {outputs['report_url']}")
            print(f"    Results: {outputs['results_url']}")
            print(f"    Analysis Code: {outputs['analysis_code_url']}")
            print(f"    Data Copy: {outputs['data_copy_url']}")
            if outputs.get('context_copy_url'):
                print(f"    Context Copy: {outputs['context_copy_url']}")

            return True

        else:
            print(f"✗ Analysis failed (HTTP {response.status_code})")
            print(f"  Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("✗ Request timed out (analysis took too long)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("White Agent A2A Service Test Suite")
    print("=" * 70)
    print(f"\nTesting service at: {BASE_URL}")

    # Test 1: Root endpoint
    if not test_root_endpoint():
        print("\n✗ Service is not responding. Make sure the server is running:")
        print("  uvicorn app.server:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # Test 2: Health check
    storage_ok = test_health_check()
    if not storage_ok:
        print("\n⚠ Warning: Storage not configured. The /run endpoint will fail.")
        print("  Set S3_BUCKET, S3_ACCESS_KEY_ID, and S3_SECRET_ACCESS_KEY")

    # Test 3: Analysis (only if you have test URLs)
    print("\n" + "=" * 70)
    print("To test the /run endpoint, you need publicly accessible URLs.")
    print("=" * 70)

    use_test_data = input("\nDo you want to test with custom URLs? (y/N): ").strip().lower()

    if use_test_data == 'y':
        context_url = input("Enter context file URL: ").strip()
        data_url = input("Enter data file URL: ").strip()
        mode = input("Enter mode (auto/llm/traditional) [auto]: ").strip() or "auto"

        test_run_analysis(context_url, data_url, mode)

    else:
        print("\nSkipping /run endpoint test.")
        print("\nTo test manually:")
        print(f"  curl -X POST {BASE_URL}/run \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{")
        print('      "context_url": "https://your-url.com/context.txt",')
        print('      "data_url": "https://your-url.com/data.csv",')
        print('      "mode": "auto"')
        print("    }'")

    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)
    print(f"\nAPI Documentation: {BASE_URL}/docs")
    print(f"Health Check: {BASE_URL}/health")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
