import sqlite3
import pandas as pd

# Conecta ao banco
conn = sqlite3.connect('ecommerce.db')

# A query que queremos testar
query = """
SELECT 
    c.customer_state, 
    ROUND(SUM(p.payment_value), 2) AS faturamento_com_frete
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN payments p ON o.order_id = p.order_id
GROUP BY c.customer_state
ORDER BY faturamento_com_frete DESC
LIMIT 3;
"""

# Roda a query e mostra o resultado
df = pd.read_sql_query(query, conn)
print("--- GABARITO DO BANCO ---")
print(df)

conn.close()