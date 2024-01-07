CREATE TABLE IF NOT EXISTS pages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content bytea,
    expires timestamp,
    uses int
);

-- drop table pages