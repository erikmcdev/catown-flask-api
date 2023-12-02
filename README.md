# Catown API

Catown API is a Flask-based API coded by me as a showcase project, designed for managing a virtual town of cats. It utilizes PostgresDB as a persistent storage solution, Alembic for database migrations, and incorporates design patterns such as Hexagonal Architecture, Test-Driven Development (TDD), and Domain-Driven Design (DDD). My potfolio React web consumes this API: https://erikdevarch.tech/houses

## Features

- **Entities:**
  - **Cat:** Represents individual cats in the town. Utilizes a `Nature` ValueObject for for coexistence compatibility logic.
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

### Repository Pattern

Abstraction over data access logic from the rest of the application, acting as a mediator between the application's business logic and the data source (such as a database).

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
   ```
## Usage
### API Endpoints
#### GET
 - /cats?house_id={house_id}: Endpoint for listing cats within a house entity
 - /houses: Listing house entities
#### POST
 - /add_cat: needs a json body with `name`, `birthdate`, `nature` and `house_id` fields, to add a cat to the DB. At the end of each transaction if there's no house with room, it automatically will create an empty one for future cats.
 - /create_house: It creates a house in case there's no one existent nor with room available.
 - /transfer: It is used for transfering cats from one house to another while keeping the correct coex coefficient in each house. It still not implemented in the front-end

## Front-end Web Application
A separate front-end web application consumes this API, providing a user-friendly interface for interacting with the API. https://erikdevarch.tech/houses
Source: https://github.com/erikmcdev/eriks-dev-archive

## License
This project is licensed under the MIT License.