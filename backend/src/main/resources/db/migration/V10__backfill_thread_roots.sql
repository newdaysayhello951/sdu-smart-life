UPDATE place_comment SET root_id=parent_id WHERE parent_id IS NOT NULL AND root_id IS NULL;
