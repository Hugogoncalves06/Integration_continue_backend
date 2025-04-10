#!/bin/bash
set -e

mongosh <<EOF
use admin
db.auth('admin', 'password')

use users_db
db.createUser({
  user: 'loise.fenoll@ynov.com',
  pwd: 'ANKymoUTFu4rbybmQ9Mt',
  roles: [
    {
      role: 'readWrite',
      db: 'users_db'
    },
    {
      role: 'userAdmin',
      db: 'users_db'
    }
  ]
})

db.administrators.insertOne({
  email: 'loise.fenoll@ynov.com',
  password: 'ANKymoUTFu4rbybmQ9Mt',
  role: 'admin'
})
EOF