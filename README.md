## Data Flow Steps

1. **Data Extraction from Online Forums**
   - **Source**: Public online forums (e.g., Reddit, discussion boards). In this case to simplify the implementation, I used the data provided by these repo:
        - https://github.com/Vicomtech/hate-speech-dataset: files contain text extracted from Stormfront, a white supremacist forum.
        - https://github.com/di-dimitrov/mmf: the train data include memes related to Covid, which may contain controversial content.
   - **Process**: A custom scraping script using BeautifulSoup which extracts comments (text) and images (e.g., JPEG, PNG) from data sources.
   - **Output**: Raw data files containing comments in txt format and images (png).

2. **Upload to Amazon S3**
   - **Input**: Raw comments and images from the scraping script.
   - **Process**: The scraping script uploads data to an Amazon S3 bucket. This should be organized by date, but simplified in this implementation for now.
   - **Output**: Raw data stored in S3, accessible via unique paths. Data is partitioned to optimize retrieval and processing

3. **External Table in Databricks**
   - **Input**: Raw data in S3 (comments and images).
   - **Process**: An external table is created in Databricks, pointing to the S3 paths (e.g., `CREATE EXTERNAL TABLE raw_data LOCATION 's3://bucket/raw/'`). This allows querying without moving data into Databricks, which will save storage cost.
   - **Output**: A queryable table in Databricks, exposing raw comments and metadata (file_name, size).

4. **Bronze Layyer/Staging Area (Deduplication)**
   - **Input**: Raw data from the Databricks external table.
   - **Process**: An ETL job in Databricks (using PySpark or SQL) deduplicates data to remove redundant comments or images (e.g., based on comment text, image hash, or unique IDs). Deduplicated data is written to a staging table (e.g., Delta Lake table).
   - **Output**: A clean, deduplicated dataset in the staging area.

5. **Silver Layer/Transformation Layer**
   - **Input**: Deduplicated data from the staging area.
   - **Process**: Databricks applies transformations, such as:
     - Cleaning: Removing invalid or incomplete records.
     - Enrichment: Adding metadata (e.g., sentiment analysis for comments, image tags via ML).
     - Normalization: Structuring data into a consistent schema.
   - **Output**: Transformed data, ready for analytical use.

6. **Gold Layer/Data Mart**
   - **Input**: Transformed data from the transformation layer.
   - **Process**: The transformed data is loaded into a data mart (e.g., Delta Lake tables or a relational database) optimized for reporting and analytics. Tables are structured for specific use cases (e.g., comment analytics, image metadata queries).
   - **Output**: Final tables in the data mart, accessible via BI tools or SQL queries.
