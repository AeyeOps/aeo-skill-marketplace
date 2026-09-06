# Debugging Tools Quick Reference

```markdown
Print/Log debugging:
  - Add log statements before and after suspect code
  - Log variable values, types, and lengths
  - Use structured logging (key=value pairs)
  - Remove debug logs after fixing (or use debug log level)

Interactive debugger:
  Python: import pdb; pdb.set_trace()  (or breakpoint())
  Node.js: debugger; statement + --inspect flag
  Java: IDE breakpoints (IntelliJ, Eclipse)

  Debugger commands (pdb):
    n (next)     — step over
    s (step)     — step into
    c (continue) — run to next breakpoint
    p expr       — print expression
    pp expr      — pretty print
    w (where)    — show stack trace
    l (list)     — show source code

Profilers (when the bug is performance):
  Python: cProfile, py-spy, line_profiler
  Node.js: --prof, clinic.js
  General: flame graphs, perf

Network debugging:
  curl -v  — verbose HTTP request/response
  dig/nslookup — DNS resolution
  traceroute — network path
  tcpdump/Wireshark — packet capture
```
