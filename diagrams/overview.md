FurrSight AI: Project Overview
1. Vision
FurrSight AI aims to revolutionize the pet grooming industry by creating the world's first large-scale, structured dataset of dog grooming transformations. By systematically collecting "before and after" imagery paired with descriptions of the services rendered, we can power a new generation of AI models capable of predicting grooming outcomes, recommending services, and educating pet owners.

2. Problem Statement
The internet is filled with unstructured data on dog grooming, including countless images and videos on platforms like YouTube, Pinterest, and Instagram. However, this data lacks the structure needed for effective machine learning. There is no readily available dataset that programmatically links a "before" photo (e.g., matted, overgrown) to an "after" photo, along with a description of the specific grooming techniques used (e.g., "lion cut," "dematting," "summer shave"). This makes it difficult to train models for specialized grooming-related tasks.

3. High-Level Plan
Our project is focused on a single primary checkpoint: creating the initial version of the FurrSight Grooming Dataset. This will be accomplished through a three-stage data pipeline.

Project Stages:

Phase 1: Query Generation

Leverage a Large Language Model (LLM) to generate thousands of diverse and creative search queries related to dog grooming.

Phase 2: Web Scraping

Deploy an automated scraper to use the generated queries on platforms like Google Images and YouTube.

The scraper will gather URLs for images, videos, and associated web page content.

Phase 3: Data Extraction & Structuring

Process the scraped content to identify and download relevant media, specifically looking for "before" and "after" image pairs.

Use a Vision-Language Model (VLM) to analyze the images and text to identify the grooming services performed.

Organize this information into a clean, structured dataset ready for model fine-tuning.

4. End Goal
The successful completion of this project will result in grooming_dataset_v1.jsonl, a file containing thousands of structured entries. This dataset will be the foundational asset for all future FurrSight AI model development, enabling us to fine-tune models that can understand the nuances of dog grooming.

