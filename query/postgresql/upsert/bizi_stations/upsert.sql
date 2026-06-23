INSERT INTO {table_name} ({col_list})
SELECT {col_list} FROM {staging_table}
ON CONFLICT (id) DO UPDATE SET {set_clause}
RETURNING (xmax = 0) AS inserted;
