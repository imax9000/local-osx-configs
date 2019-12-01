# `sudo` with Touch ID

This role will add Touch ID as a sufficient option to authenticate for `sudo`.
If `pam_reattach` is installed, it will also add that - this is needed to make
`sudo` prompts show up properly from inside `tmux`.
