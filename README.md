# ESL_back

## Data Model

<br />
For Rental Car application we’ll need to persist data about potential users and cars offered

DB → Dynamo DB

Dynamo DB is the chosen tech to store the data because it is easy to scale, flexible as it is a non-sql db, and integrates easily with the tech stack of the project.

**PK** : primary key

**SK**: sort key

### Entity Model:

<br />

**Reservation**

- ReservationId (PK)
- userId(SK)
- carId
- status
- start date
- end date
- register Date

**User**

- userId (PK)
- name
- id
- is admin
- email
- age
- register date

**Car**

- carId (PK)
- brand (SK)
- model
- license
- pictures (object key + bucket where car’s pictures are stored)
- register date

<br />

## API Design

<br />

## User

---

**POST /v1/users**
<br />

> Create User

---

---

**GET /v1/users**
<br />

> Get All Users information

---

---

**GET /v1/users/:userid**
<br />

> Get User information

---

---

**PUT /v1/user/:userid**
<br />

> Update User

---

---

**DELETE /v1/user/:userid**
<br />

> Delete User

---

<br />
<br />

## Car

---

**POST /v1/cars**
<br />

> Create car

---

---

**GET /v1/cars**
<br />

> Get all cars information

---

---

**GET /v1/cars/:carid**
<br />

> Get car information

---

---

**PUT /v1/car/:carid**
<br />

> Update car

---

---

**DELETE /v1/car/:carid**
<br />

> Delete car

---

<br />
<br />

## Reservations

## <br />

**POST /v1/car/:carid/reservations**
<br />

> Create reservation for a car

---

---

**GET /v1/car/:carid/reservations**
<br />

> Get all reservations on car

---

---

**GET /v1/car/:carid/reservations/:reservationid**
<br />

> Get reservation by carid

---

---

**PUT /v1/car/:carid/reservations/:reservationid**
<br />

> Update reservation by id

---

---

**DELETE /v1/car/:carid/reservations/:reservationid**
<br />

> Delete reservation by id

---
