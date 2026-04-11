-- 1. Create Tables
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    city TEXT,
    total_purchase_amount NUMERIC DEFAULT 0,
    date_joined DATE DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC NOT NULL,
    stock_quantity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE,
    product_category TEXT NOT NULL,
    order_amount NUMERIC NOT NULL,
    order_date DATE DEFAULT now(),
    status TEXT CHECK (status IN ('Completed', 'Pending', 'Cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 2. Enable RLS
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

-- 3. Create Public Anon Policy (for demo purposes)
CREATE POLICY "Public Anon Access" ON public.customers FOR ALL USING (true);
CREATE POLICY "Public Anon Access" ON public.orders FOR ALL USING (true);
CREATE POLICY "Public Anon Access" ON public.products FOR ALL USING (true);

-- 4. Seed Data
-- 20 Sample Customers
INSERT INTO public.customers (name, email, phone, city, total_purchase_amount, date_joined) VALUES
('John Doe', 'john@example.com', '1234567890', 'New York', 1200, '2023-01-15'),
('Jane Smith', 'jane@example.com', '2345678901', 'Los Angeles', 850, '2023-02-10'),
('Alice Brown', 'alice@example.com', '3456789012', 'Chicago', 2100, '2023-03-05'),
('Bob Johnson', 'bob@example.com', '4567890123', 'Houston', 450, '2023-04-12'),
('Charlie Davis', 'charlie@example.com', '5678901234', 'Phoenix', 1500, '2023-05-20'),
('Diana Prince', 'diana@example.com', '6789012345', 'Philadelphia', 3000, '2023-06-15'),
('Edward Norton', 'edward@example.com', '7890123456', 'San Antonio', 700, '2023-07-01'),
('Fiona Apple', 'fiona@example.com', '8901234567', 'San Diego', 1100, '2023-08-10'),
('George Carlin', 'george@example.com', '9012345678', 'Dallas', 900, '2023-09-05'),
('Hannah Abbott', 'hannah@example.com', '0123456789', 'San Jose', 400, '2023-10-12'),
('Ian Wright', 'ian@example.com', '1122334455', 'Austin', 1800, '2023-11-20'),
('Julia Roberts', 'julia@example.com', '2233445566', 'Jacksonville', 2500, '2023-12-15'),
('Kevin Hart', 'kevin@example.com', '3344556677', 'Fort Worth', 600, '2024-01-10'),
('Laura Palmer', 'laura@example.com', '4455667788', 'Columbus', 1300, '2024-02-05'),
('Mike Wazowski', 'mike@example.com', '5566778899', 'Charlotte', 200, '2024-03-12'),
('Nina Simone', 'nina@example.com', '6677889900', 'San Francisco', 5000, '2024-03-20'),
('Oscar Wilde', 'oscar@example.com', '7788990011', 'Indianapolis', 150, '2024-04-01'),
('Peter Parker', 'peter@example.com', '8899001122', 'Seattle', 950, '2024-04-05'),
('Quinn Fabray', 'quinn@example.com', '9900112233', 'Denver', 1250, '2024-04-08'),
('Riley Reid', 'riley@example.com', '0011223344', 'Washington', 3200, '2024-04-10');

-- 50 Sample Orders (using category text as specified)
INSERT INTO public.orders (customer_id, product_category, order_amount, order_date, status)
SELECT 
    id, 
    (ARRAY['Electronics', 'Clothing', 'Food', 'Furniture', 'Sports'])[floor(random() * 5 + 1)],
    floor(random() * 500 + 20),
    CURRENT_DATE - (floor(random() * 365) || ' days')::interval,
    (ARRAY['Completed', 'Pending', 'Cancelled'])[floor(random() * 3 + 1)]
FROM public.customers
CROSS JOIN generate_series(1, 2) -- Ensures 40 orders (2 per customer approx)
UNION ALL
SELECT 
    id, 
    (ARRAY['Electronics', 'Clothing', 'Food', 'Furniture', 'Sports'])[floor(random() * 5 + 1)],
    floor(random() * 500 + 20),
    CURRENT_DATE - (floor(random() * 30) || ' days')::interval,
    (ARRAY['Completed', 'Pending', 'Cancelled'])[floor(random() * 3 + 1)]
FROM (SELECT id FROM public.customers LIMIT 10) AS sub -- Adds 10 more to make 50
;

-- Products (optional but useful for the schema)
INSERT INTO public.products (name, category, price, stock_quantity) VALUES
('Smartphone', 'Electronics', 699, 50),
('Laptop', 'Electronics', 1200, 30),
('T-Shirt', 'Clothing', 25, 200),
('Jeans', 'Clothing', 50, 150),
('Pizza', 'Food', 15, 100),
('Burger', 'Food', 10, 120),
('Table', 'Furniture', 150, 20),
('Chair', 'Furniture', 80, 45),
('Football', 'Sports', 30, 80),
('Tennis Racket', 'Sports', 120, 25);
