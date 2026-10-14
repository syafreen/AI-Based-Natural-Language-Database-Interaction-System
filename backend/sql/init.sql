CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total_cents INTEGER NOT NULL CHECK (total_cents >= 0),
    status TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO users (email, name)
VALUES
    ('ada@example.com', 'Ada Lovelace'),
    ('grace@example.com', 'Grace Hopper')
ON CONFLICT (email) DO NOTHING;

INSERT INTO orders (user_id, total_cents, status)
SELECT users.id, seed.total_cents, seed.status
FROM (
    VALUES
        ('ada@example.com', 12900, 'paid'),
        ('ada@example.com', 5400, 'shipped'),
        ('grace@example.com', 8800, 'pending')
) AS seed(email, total_cents, status)
JOIN users ON users.email = seed.email;
