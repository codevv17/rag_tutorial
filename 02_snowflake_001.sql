USE ROLE ACCOUNTADMIN;

CREATE DATABASE IF NOT EXISTS MCP_DEMO;
CREATE SCHEMA IF NOT EXISTS MCP_DEMO.SEMANTIC;

USE DATABASE MCP_DEMO;
USE SCHEMA SEMANTIC;

CREATE OR REPLACE SEMANTIC VIEW tpch_sf10_analysis
  TABLES (
    region AS SNOWFLAKE_SAMPLE_DATA.TPCH_SF10.REGION
      PRIMARY KEY (r_regionkey),

    nation AS SNOWFLAKE_SAMPLE_DATA.TPCH_SF10.NATION
      PRIMARY KEY (n_nationkey),

    customer AS SNOWFLAKE_SAMPLE_DATA.TPCH_SF10.CUSTOMER
      PRIMARY KEY (c_custkey),

    orders AS SNOWFLAKE_SAMPLE_DATA.TPCH_SF10.ORDERS
      PRIMARY KEY (o_orderkey),

    lineitem AS SNOWFLAKE_SAMPLE_DATA.TPCH_SF10.LINEITEM
      PRIMARY KEY (l_orderkey, l_linenumber),

    supplier AS SNOWFLAKE_SAMPLE_DATA.TPCH_SF10.SUPPLIER
      PRIMARY KEY (s_suppkey)
  )

  RELATIONSHIPS (
    nation   (n_regionkey) REFERENCES region,
    customer (c_nationkey) REFERENCES nation,
    orders   (o_custkey)   REFERENCES customer,
    lineitem (l_orderkey)  REFERENCES orders,
    supplier (s_nationkey) REFERENCES nation
  )

  FACTS (
    region.r_name AS r_name,
    nation.n_name AS n_name,
    orders.o_orderkey AS o_orderkey,
    orders.o_totalprice AS o_totalprice,
    lineitem.l_quantity AS l_quantity,
    lineitem.l_extendedprice AS l_extendedprice,
    lineitem.l_discount AS l_discount,
    lineitem.l_tax AS l_tax,
    lineitem.line_item_id AS CONCAT(l_orderkey, '-', l_linenumber),
    orders.count_line_items AS COUNT(lineitem.line_item_id),
    customer.c_customer_order_count AS COUNT(orders.o_orderkey)
  )

  DIMENSIONS (
    region.region_name AS r_name,
    nation.nation_name AS n_name,
    customer.customer_name AS c_name,
    customer.customer_region_name AS region.r_name,
    customer.customer_nation_name AS nation.n_name,
    customer.customer_market_segment AS c_mktsegment,
    customer.customer_country_code AS LEFT(c_phone, 2),
    orders.order_date AS o_orderdate,
    orders.order_priority AS o_orderpriority,
    orders.order_status AS o_orderstatus
  )

  METRICS (
    customer.customer_count AS COUNT(c_custkey),
    customer.customer_order_count AS SUM(c_customer_order_count),
    orders.order_count AS COUNT(o_orderkey),
    orders.total_order_value AS SUM(o_totalprice),
    orders.average_order_value AS AVG(o_totalprice),
    orders.average_line_items_per_order AS AVG(count_line_items),
    lineitem.total_extended_price AS SUM(l_extendedprice),
    lineitem.total_discount_amount AS SUM(l_extendedprice * l_discount),
    supplier.supplier_count AS COUNT(s_suppkey)
  );




CREATE OR REPLACE MCP SERVER MCP_DEMO.SEMANTIC.TPCH_MCP_SERVER
FROM SPECIFICATION $$
tools:
  - name: "tpch_analyst"
    title: "TPCH SF10 Analyst"
    type: "CORTEX_ANALYST_MESSAGE"
    identifier: "MCP_DEMO.SEMANTIC.TPCH_SF10_ANALYSIS"
    description: "Answer natural language questions about Snowflake TPCH_SF10 customers, orders, lineitems, suppliers, nations, and regions."

  - name: "tpch_sql_exec"
    title: "TPCH SQL Execution"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute read-only SQL against Snowflake for TPCH analysis."
    config:
      read_only: true
      query_timeout: 120
      warehouse: "COMPUTE_WH"
$$;



USE ROLE ACCOUNTADMIN;

CREATE ROLE IF NOT EXISTS MCP_TPCH_ROLE;

GRANT USAGE ON DATABASE MCP_DEMO TO ROLE MCP_TPCH_ROLE;
GRANT USAGE ON SCHEMA MCP_DEMO.SEMANTIC TO ROLE MCP_TPCH_ROLE;

GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE MCP_TPCH_ROLE;

GRANT USAGE ON MCP SERVER MCP_DEMO.SEMANTIC.TPCH_MCP_SERVER TO ROLE MCP_TPCH_ROLE;

GRANT SELECT ON SEMANTIC VIEW MCP_DEMO.SEMANTIC.TPCH_SF10_ANALYSIS TO ROLE MCP_TPCH_ROLE;

GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_SAMPLE_DATA TO ROLE MCP_TPCH_ROLE;

GRANT ROLE MCP_TPCH_ROLE TO USER VIPULSH;

ALTER USER VIPULSH
SET DEFAULT_ROLE = MCP_TPCH_ROLE
    DEFAULT_WAREHOUSE = COMPUTE_WH;


-- PAT 
ALTER USER IF EXISTS VIPULSH
ADD PROGRAMMATIC ACCESS TOKEN tpch_mcp_token
  ROLE_RESTRICTION = 'MCP_TPCH_ROLE'
  DAYS_TO_EXPIRY = 30
  COMMENT = 'PAT for Snowflake MCP TPCH demo';

-- Allow IP
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE NETWORK RULE VIPULSH_LOCAL_IP_RULE
  MODE = INGRESS
  TYPE = IPV4
  VALUE_LIST = ('99.xxx.xxx.30');

CREATE OR REPLACE NETWORK POLICY VIPULSH_PAT_POLICY
  ALLOWED_NETWORK_RULE_LIST = ('VIPULSH_LOCAL_IP_RULE');

ALTER USER VIPULSH
SET NETWORK_POLICY = VIPULSH_PAT_POLICY;