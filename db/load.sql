\COPY Users FROM 'users.csv' WITH DELIMITER ',' NULL '' CSV
    SELECT pg_catalog.setval('public.users_uid_seq',
                         (SELECT MAX(uid)+1 FROM Users),
                         false);

\COPY Products FROM 'products.csv' WITH DELIMITER ',' NULL '' CSV
    SELECT pg_catalog.setval('public.products_pid_seq',
                         (SELECT MAX(pid)+1 FROM Products),
                         false);

\COPY Categories FROM 'categories.csv' WITH DELIMITER ',' NULL '' CSV
\COPY HasInCart FROM 'has_in_cart.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Orders FROM 'orders.csv' WITH DELIMITER ',' NULL '' CSV
    
\COPY Reviews_Product FROM 'reviews_product.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Reviews_Seller FROM 'reviews_seller.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sells FROM 'sells.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Coupons FROM 'coupons.csv' WITH DELIMITER ',' NULL '' CSV
