#!/usr/bin/env sh
#
# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: Apache-2.0

until rc alias set local http://s3:9000 "$RUSTFS_ACCESS_KEY" "$RUSTFS_SECRET_KEY"; do
  echo "RustFS is not ready yet, retrying in 2 seconds..."
  sleep 2
done

echo "create private bucket \"trainings\""
rc mb local/trainings

echo "RustFS Configuration Complete!"
