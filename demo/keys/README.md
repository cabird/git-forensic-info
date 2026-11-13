# Demo signing key

`ada-demo-signing-key.asc` is a **throwaway GPG private key, public on purpose**.
It belongs to the fictional "Ada Example" and exists only so that
`demo/make_demo.sh` can sign the demo's release commit with the same key on
every run, which keeps that commit's hash stable. It protects nothing. Never
import it into a real keyring or trust anything it signs.

It was generated once with:

    gpg --batch --faked-system-time 20240101T000000 --passphrase '' \
        --quick-generate-key 'Ada Example <ada@example.com>' ed25519 sign never
