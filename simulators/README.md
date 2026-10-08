# Simulators

Create one folder per simulator, using a stable name such as `simulators/<simulator-name>/`. Put that simulator's setup notes, scripts, project configuration, and evaluation code inside it.

No simulator installation or historical project pack has been imported yet. Before running, document the selected version, upstream revision, setup steps, GPU and driver requirements, OS compatibility, and exact evaluation plan. Keep downloaded engines and large dependencies outside tracked source files.

Write run records and reviewable results to `results/<simulator-name>/<run-id>/`. Store large captures in ignored `artifacts/` locally or durable storage and link them from the run record. Commit and synchronize authored code and notes between the local checkout and the rented instance.
