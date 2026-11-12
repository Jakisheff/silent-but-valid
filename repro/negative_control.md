# Negative control: an honest, loud failure

During the same two days the disk filled up and the Rust linker failed:

    error: failed to write to `.../deps/rmeta...`: No space left on device (os error 28)

This is the control case: the failure was loud (non-zero exit, clear
message, immediate CI signal), correctly attributed (disk, not code), and
cheap to act on. Nothing about it looked valid. The five cases in this
dataset are interesting precisely because they share none of these
properties: every one of them produced a success-shaped signal.
