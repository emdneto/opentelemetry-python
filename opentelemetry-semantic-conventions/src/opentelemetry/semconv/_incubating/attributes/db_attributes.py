# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from typing import Final

DB_CASSANDRA_CONSISTENCY_LEVEL: Final = "db.cassandra.consistency_level"
"""
The consistency level of the query. Based on consistency values from [CQL](https://docs.datastax.com/en/cassandra-oss/3.0/cassandra/dml/dmlConfigConsistency.html).
"""

DB_CASSANDRA_COORDINATOR_DC: Final = "db.cassandra.coordinator.dc"
"""
The data center of the coordinating node for a query.
"""

DB_CASSANDRA_COORDINATOR_ID: Final = "db.cassandra.coordinator.id"
"""
The ID of the coordinating node for a query.
"""

DB_CASSANDRA_IDEMPOTENCE: Final = "db.cassandra.idempotence"
"""
Whether or not the query is idempotent.
"""

DB_CASSANDRA_PAGE_SIZE: Final = "db.cassandra.page_size"
"""
The fetch size used for paging, i.e. how many rows will be returned at once.
"""

DB_CASSANDRA_SPECULATIVE_EXECUTION_COUNT: Final = (
    "db.cassandra.speculative_execution_count"
)
"""
The number of times a query was speculatively executed. Not set or `0` if the query was not executed speculatively.
"""

DB_CASSANDRA_TABLE: Final = "db.cassandra.table"
"""
Deprecated: Replaced by `db.collection.name`.
"""

DB_CLIENT_CONNECTIONS_POOL_NAME: Final = "db.client.connections.pool.name"
"""
The name of the connection pool; unique within the instrumented application. In case the connection pool implementation doesn't provide a name, instrumentation should use a combination of `server.address` and `server.port` attributes formatted as `server.address:server.port`.
"""

DB_CLIENT_CONNECTIONS_STATE: Final = "db.client.connections.state"
"""
The state of a connection in the pool.
"""

DB_COLLECTION_NAME: Final = "db.collection.name"
"""
The name of a collection (table, container) within the database.
Note: If the collection name is parsed from the query, it SHOULD match the value provided in the query and may be qualified with the schema and database name.
    It is RECOMMENDED to capture the value as provided by the application without attempting to do any case normalization.
"""

DB_CONNECTION_STRING: Final = "db.connection_string"
"""
Deprecated: "Replaced by `server.address` and `server.port`.".
"""

DB_COSMOSDB_CLIENT_ID: Final = "db.cosmosdb.client_id"
"""
Unique Cosmos client instance id.
"""

DB_COSMOSDB_CONNECTION_MODE: Final = "db.cosmosdb.connection_mode"
"""
Cosmos client connection mode.
"""

DB_COSMOSDB_CONTAINER: Final = "db.cosmosdb.container"
"""
Deprecated: Replaced by `db.collection.name`.
"""

DB_COSMOSDB_OPERATION_TYPE: Final = "db.cosmosdb.operation_type"
"""
CosmosDB Operation Type.
"""

DB_COSMOSDB_REQUEST_CHARGE: Final = "db.cosmosdb.request_charge"
"""
RU consumed for that operation.
"""

DB_COSMOSDB_REQUEST_CONTENT_LENGTH: Final = (
    "db.cosmosdb.request_content_length"
)
"""
Request payload size in bytes.
"""

DB_COSMOSDB_STATUS_CODE: Final = "db.cosmosdb.status_code"
"""
Cosmos DB status code.
"""

DB_COSMOSDB_SUB_STATUS_CODE: Final = "db.cosmosdb.sub_status_code"
"""
Cosmos DB sub status code.
"""

DB_ELASTICSEARCH_CLUSTER_NAME: Final = "db.elasticsearch.cluster.name"
"""
Represents the identifier of an Elasticsearch cluster.
"""

DB_ELASTICSEARCH_NODE_NAME: Final = "db.elasticsearch.node.name"
"""
Represents the human-readable identifier of the node/instance to which a request was routed.
"""

DB_ELASTICSEARCH_PATH_PARTS_TEMPLATE: Final = "db.elasticsearch.path_parts"
"""
A dynamic value in the url path.
Note: Many Elasticsearch url paths allow dynamic values. These SHOULD be recorded in span attributes in the format `db.elasticsearch.path_parts.<key>`, where `<key>` is the url path part name. The implementation SHOULD reference the [elasticsearch schema](https://raw.githubusercontent.com/elastic/elasticsearch-specification/main/output/schema/schema.json) in order to map the path part values to their names.
"""

DB_INSTANCE_ID: Final = "db.instance.id"
"""
Deprecated: Deprecated, no general replacement at this time. For Elasticsearch, use `db.elasticsearch.node.name` instead.
"""

DB_JDBC_DRIVER_CLASSNAME: Final = "db.jdbc.driver_classname"
"""
Deprecated: Removed as not used.
"""

DB_MONGODB_COLLECTION: Final = "db.mongodb.collection"
"""
Deprecated: Replaced by `db.collection.name`.
"""

DB_MSSQL_INSTANCE_NAME: Final = "db.mssql.instance_name"
"""
Deprecated: Deprecated, no replacement at this time.
"""

DB_NAME: Final = "db.name"
"""
Deprecated: Replaced by `db.namespace`.
"""

DB_NAMESPACE: Final = "db.namespace"
"""
The name of the database, fully qualified within the server address and port.
Note: If a database system has multiple namespace components, they SHOULD be concatenated (potentially using database system specific conventions) from most general to most specific namespace component, and more specific namespaces SHOULD NOT be captured without the more general namespaces, to ensure that "startswith" queries for the more general namespaces will be valid.
    Semantic conventions for individual database systems SHOULD document what `db.namespace` means in the context of that system.
    It is RECOMMENDED to capture the value as provided by the application without attempting to do any case normalization.
"""

DB_OPERATION: Final = "db.operation"
"""
Deprecated: Replaced by `db.operation.name`.
"""

DB_OPERATION_NAME: Final = "db.operation.name"
"""
The name of the operation or command being executed.
Note: It is RECOMMENDED to capture the value as provided by the application without attempting to do any case normalization.
"""

DB_QUERY_PARAMETER_TEMPLATE: Final = "db.query.parameter"
"""
The query parameters used in `db.query.text`, with `<key>` being the parameter name, and the attribute value being the parameter value.
Note: Query parameters should only be captured when `db.query.text` is parameterized with placeholders.
    If a parameter has no name and instead is referenced only by index, then `<key>` SHOULD be the 0-based index.
"""

DB_QUERY_TEXT: Final = "db.query.text"
"""
The database query being executed.
"""

DB_REDIS_DATABASE_INDEX: Final = "db.redis.database_index"
"""
Deprecated: Replaced by `db.namespace`.
"""

DB_SQL_TABLE: Final = "db.sql.table"
"""
Deprecated: Replaced by `db.collection.name`.
"""

DB_STATEMENT: Final = "db.statement"
"""
Deprecated: Replaced by `db.query.text`.
"""

DB_SYSTEM: Final = "db.system"
"""
The database management system (DBMS) product as identified by the client instrumentation.
Note: The actual DBMS may differ from the one identified by the client. For example, when using PostgreSQL client libraries to connect to a CockroachDB, the `db.system` is set to `postgresql` based on the instrumentation's best knowledge.
"""

DB_USER: Final = "db.user"
"""
Deprecated: No replacement at this time.
"""


class DbCassandraConsistencyLevelValues(Enum):
    ALL = "all"
    """all."""
    EACH_QUORUM = "each_quorum"
    """each_quorum."""
    QUORUM = "quorum"
    """quorum."""
    LOCAL_QUORUM = "local_quorum"
    """local_quorum."""
    ONE = "one"
    """one."""
    TWO = "two"
    """two."""
    THREE = "three"
    """three."""
    LOCAL_ONE = "local_one"
    """local_one."""
    ANY = "any"
    """any."""
    SERIAL = "serial"
    """serial."""
    LOCAL_SERIAL = "local_serial"
    """local_serial."""


class DbClientConnectionsStateValues(Enum):
    IDLE = "idle"
    """idle."""
    USED = "used"
    """used."""


class DbCosmosdbConnectionModeValues(Enum):
    GATEWAY = "gateway"
    """Gateway (HTTP) connections mode."""
    DIRECT = "direct"
    """Direct connection."""


class DbCosmosdbOperationTypeValues(Enum):
    INVALID = "Invalid"
    """invalid."""
    CREATE = "Create"
    """create."""
    PATCH = "Patch"
    """patch."""
    READ = "Read"
    """read."""
    READ_FEED = "ReadFeed"
    """read_feed."""
    DELETE = "Delete"
    """delete."""
    REPLACE = "Replace"
    """replace."""
    EXECUTE = "Execute"
    """execute."""
    QUERY = "Query"
    """query."""
    HEAD = "Head"
    """head."""
    HEAD_FEED = "HeadFeed"
    """head_feed."""
    UPSERT = "Upsert"
    """upsert."""
    BATCH = "Batch"
    """batch."""
    QUERY_PLAN = "QueryPlan"
    """query_plan."""
    EXECUTE_JAVASCRIPT = "ExecuteJavaScript"
    """execute_javascript."""


class DbSystemValues(Enum):
    OTHER_SQL = "other_sql"
    """Some other SQL database. Fallback only. See notes."""
    MSSQL = "mssql"
    """Microsoft SQL Server."""
    MSSQLCOMPACT = "mssqlcompact"
    """Microsoft SQL Server Compact."""
    MYSQL = "mysql"
    """MySQL."""
    ORACLE = "oracle"
    """Oracle Database."""
    DB2 = "db2"
    """IBM Db2."""
    POSTGRESQL = "postgresql"
    """PostgreSQL."""
    REDSHIFT = "redshift"
    """Amazon Redshift."""
    HIVE = "hive"
    """Apache Hive."""
    CLOUDSCAPE = "cloudscape"
    """Cloudscape."""
    HSQLDB = "hsqldb"
    """HyperSQL DataBase."""
    PROGRESS = "progress"
    """Progress Database."""
    MAXDB = "maxdb"
    """SAP MaxDB."""
    HANADB = "hanadb"
    """SAP HANA."""
    INGRES = "ingres"
    """Ingres."""
    FIRSTSQL = "firstsql"
    """FirstSQL."""
    EDB = "edb"
    """EnterpriseDB."""
    CACHE = "cache"
    """InterSystems Caché."""
    ADABAS = "adabas"
    """Adabas (Adaptable Database System)."""
    FIREBIRD = "firebird"
    """Firebird."""
    DERBY = "derby"
    """Apache Derby."""
    FILEMAKER = "filemaker"
    """FileMaker."""
    INFORMIX = "informix"
    """Informix."""
    INSTANTDB = "instantdb"
    """InstantDB."""
    INTERBASE = "interbase"
    """InterBase."""
    MARIADB = "mariadb"
    """MariaDB."""
    NETEZZA = "netezza"
    """Netezza."""
    PERVASIVE = "pervasive"
    """Pervasive PSQL."""
    POINTBASE = "pointbase"
    """PointBase."""
    SQLITE = "sqlite"
    """SQLite."""
    SYBASE = "sybase"
    """Sybase."""
    TERADATA = "teradata"
    """Teradata."""
    VERTICA = "vertica"
    """Vertica."""
    H2 = "h2"
    """H2."""
    COLDFUSION = "coldfusion"
    """ColdFusion IMQ."""
    CASSANDRA = "cassandra"
    """Apache Cassandra."""
    HBASE = "hbase"
    """Apache HBase."""
    MONGODB = "mongodb"
    """MongoDB."""
    REDIS = "redis"
    """Redis."""
    COUCHBASE = "couchbase"
    """Couchbase."""
    COUCHDB = "couchdb"
    """CouchDB."""
    COSMOSDB = "cosmosdb"
    """Microsoft Azure Cosmos DB."""
    DYNAMODB = "dynamodb"
    """Amazon DynamoDB."""
    NEO4J = "neo4j"
    """Neo4j."""
    GEODE = "geode"
    """Apache Geode."""
    ELASTICSEARCH = "elasticsearch"
    """Elasticsearch."""
    MEMCACHED = "memcached"
    """Memcached."""
    COCKROACHDB = "cockroachdb"
    """CockroachDB."""
    OPENSEARCH = "opensearch"
    """OpenSearch."""
    CLICKHOUSE = "clickhouse"
    """ClickHouse."""
    SPANNER = "spanner"
    """Cloud Spanner."""
    TRINO = "trino"
    """Trino."""
