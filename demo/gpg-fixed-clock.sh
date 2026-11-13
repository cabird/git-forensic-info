#!/bin/sh
# Used as gpg.program by make_demo.sh. Signing runs with a frozen clock so the
# demo's signed commit gets the same signature (and so the same hash) on every
# rebuild. Verification runs normally.
case " $* " in
  *" --verify "*) exec gpg "$@" ;;
  *) exec gpg --faked-system-time "${DEMO_SIGN_TIME}!" "$@" ;;
esac
