# Pose camera mounting correction

The first two completed A sequences used `DownCamera` at `xyz=0 0 0.5`, `rpy-deg=0 -11.46 0` and `ForwardCamera` at frame origin. Inspection after the two runs found that the nominal downward camera was only tilted 11.46° in the pose config. Its captures remain valid evidence of pose setting and timestamp freshness but are not a nadir capture baseline.

The flight config independently used `DownCamera` at `xyz=0 0 0`, `rpy-deg=0 -90 0`. A separate corrected A attempt changes only the pose config's `DownCamera` mount to that transform, after the two original sequences and both measured B repeats. It has its own run ID, config hash and result. Do not aggregate pixels or camera poses across the original and corrected A configs. The corrected attempt is one diagnosed repair, not an extra planned repeat.
