"""White Agent for RCT Analysis.

An AgentBeats-compatible agent that performs statistical analysis on
randomized controlled experiments and generates comprehensive reports.
"""

from .agent import WhiteAgent
from .analyzer import RCTAnalyzer
from .report_generator import ReportGenerator

__all__ = ['WhiteAgent', 'RCTAnalyzer', 'ReportGenerator']
