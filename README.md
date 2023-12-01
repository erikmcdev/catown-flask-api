# Catown API

Catown API is a Flask-based API designed for managing a virtual town of cats. It utilizes PostgresDB as a persistent storage solution, Alembic for database migrations, and incorporates design patterns such as Hexagonal Architecture, Test-Driven Development (TDD), and Domain-Driven Design (DDD). There's a front end react web that consumes this API: 

## Features

- **Entities:**
  - **Cat:** Represents individual cats in the town. Utilizes a `Nature` ValueObject for compatibility logic.
  - **House:** Represents a dwelling where cats reside. Each house can accommodate up to 4 cats.
  
- **Coexistence Coefficient:**
  - The coexistence coefficient dynamically changes as cats join or leave a house with more than one cat.

## Tech Stack

- **Flask:** The web framework used for building the API.
- **PostgresDB:** The chosen relational database for persistent storage.
- **Alembic:** Used for managing database migrations.
- **Docker Compose:** Easily run the project in a local environment.

## Design Patterns

### Hexagonal Architecture

The project follows the principles of Hexagonal Architecture, emphasizing a clear separation between the application core and the external interfaces.

### Test-Driven Development (TDD)

The development process is guided by Test-Driven Development to ensure the reliability and correctness of the codebase. Tests cover different aspects of the application, including unit tests, integration tests, and end-to-end tests.

### Domain-Driven Design (DDD)

Domain-Driven Design concepts are applied to create a rich and expressive domain model that accurately represents the problem space of managing a community of cats.

### Unit of Work (UOW) Pattern

The Unit of Work pattern is used to abstract atomicity over persistent operations, ensuring consistency during database interactions.

## Getting Started

### Prerequisites

- Python 3.x
- Docker
- Docker Compose

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/erikmcdev/catown-flask-api.git
   cd catown-flask-api
   ```
   
2. Start the Docker compose services:

   ```bash
   docker compose up -d
