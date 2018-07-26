# -*- coding: utf-8 -*-

from .exc import log_exception
from .trace import start_trace, stop_trace
from .trace import TraceLogger
from .trace import TRACE_CALL, TRACE_ALL
from .logger import Log

log = Log()

