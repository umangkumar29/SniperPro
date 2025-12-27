#!/bin/bash
# Update pg_hba.conf to allow trust authentication from all hosts
cat > /var/lib/postgresql/data/pg_hba.conf << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             0.0.0.0/0               trust
host    all             all             ::1/128                 trust
host    all             all             ::/0                    trust
EOF

# Reload PostgreSQL configuration
pg_ctl reload
