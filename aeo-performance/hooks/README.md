# Performance - Monitoring and Cost Tracking Hooks

Performance monitoring, cost tracking, and efficiency optimization hooks for Claude Code operations.

## Event Mapping Caveats

| Original Event | New Mapping | Notes |
|---------------|-------------|-------|
| `PreToolUse` | `PreToolUse` (kept) | Already compliant structure. |
| `PostToolUse` | `PostToolUse` (kept) | Already compliant structure. |
| `SubagentStop` | `SubagentStop` (kept) | Wrapped flat array in correct `matcher`/`hooks` structure. |
| `Stop` | `Stop` (kept) | Wrapped flat array in correct `matcher`/`hooks` structure. |

## Metrics

### Performance Metrics
- **Response time:** Time between request and response
- **Throughput:** Operations completed per minute
- **Latency:** P50, P95, P99 latency percentiles
- **Error rate:** Errors per 100 operations
- **Resource usage:** CPU, memory, disk I/O

### Cost Tracking
| Model | Input | Output |
|-------|-------|--------|
| Sonnet | $0.003 per 1K tokens | $0.015 per 1K tokens |
| Opus | $0.015 per 1K tokens | $0.075 per 1K tokens |

Additional cost factors: API calls, agent execution time, web searches.

### Efficiency Metrics
- Cache hit rate
- Duplicate operations count
- Unnecessary reads (files read but not modified)
- Optimization opportunities

## Monitoring Scripts

### calculate_agent_cost.py
Calculates agent execution cost based on model type and duration. Logs to `.claude/cost_tracking.json`.

### generate_performance_report.py
Parses `.claude/performance.log` and generates statistics (count, mean, median, P95) per operation type. Output: `.claude/performance_report.json`.

### identify_bottlenecks.py
Reads the performance report and flags operations with P95 latency exceeding 1000ms.

## Dashboards

### Grafana
- Datasource: Prometheus
- Panels: Response time histogram, Token usage over time, Cost breakdown by model, Error rate graph, Agent execution times

### Custom Dashboard
- URL: `http://localhost:3000/claude-metrics`
- Refresh interval: 30s
- Alerts: High error rate (>5%), Slow response time (>5s), Cost spike (>$10/hour), Memory usage (>80%)

## Optimization Rules

| Condition | Action | Estimated Savings |
|-----------|--------|-------------------|
| Same file read >3 times | Suggest caching | ~30% token reduction |
| Opus model used for simple task | Suggest switching to Sonnet | ~80% cost reduction |
| Large file reads (>10K lines) | Suggest targeted grep/search | ~50% token reduction |
| Repeated similar operations | Suggest batch processing | ~40% time reduction |

## Notes
- Adjust cost calculations based on current pricing
- Set up alerting for cost or performance thresholds
- Review metrics weekly to identify optimization opportunities
- Consider implementing caching for frequently accessed resources
