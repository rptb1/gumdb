#!/bin/sh
#
# $Id$

# Empty message
python import.py <<EOF
EOF

# Non-parseable date field
python import.py <<EOF
Message-Id: <test-message-id-1>
Date: non-parseable
EOF

# Duplicate message
python import.py <<EOF
Message-Id: <test-mesage-id-2>
Date: Mon, Oct 09 2000 20:50:37 +0100

duplicate
EOF
python import.py <<EOF
Message-Id: <test-mesage-id-2>
Date: Mon, Oct 09 2000 20:50:37 +0100

duplicate
EOF

# Duplicate Message-Id with different message
python import.py <<EOF
Message-Id: <test-mesage-id-3>
Date: Mon, Oct 09 2000 20:50:37 +0100

Duplicate
EOF
python import.py <<EOF
Message-Id: <test-mesage-id-3>
Date: Mon, Oct 09 2000 20:50:37 +0100

Duplicate Message-Id but different!
EOF
