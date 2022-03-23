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
- start date 
- end date
- register Date

**User** 

- userId (PK) 
- name
- is admin
- email 
- age 
- register date

**Car** 

- carId (PK) 
- brand  (SK)
- model 
- license 
- pictures (object key + bucket where car’s pictures are stored)
- register date

<br />

## API Design
<br />

## User
---

**POST /v1/user**
<br />
>Create User

---
---

**GET /v1/user/:id**
<br />
>Get User information

---
---

**PUT /v1/user/:id**
<br />
>Update User

---
---

**DELETE /v1/user/:id**
<br />
>Delete User

---
<br />
<br />

## Car

---

**POST /v1/car**
<br />
>Create car

---
---

**GET /v1/car/:carid**
<br />
>Get car information

---
---

**PUT /v1/car/:carid**
<br />
>Update car

---
---

**DELETE /v1/car/:carid**
<br />
>Delete car

---

<br />
<br />

## Reservations
<br />
---

**POST /v1/car/:carid/reservation**
<br />
>Create reservation for a car

---
---

**GET /v1/car/:carid/reservation**
<br />
>Get all reservations on car

---
---

**GET /v1/car/:carid/reservation/:reservationid**
<br />
>Get reservation by carid

---
---

**PUT /v1/car/:carid/reservation/:reservationid**
<br />
>Update reservation by id

---
---

**DELETE /v1/car/:carid/reservation/:reservationid**
<br />
>Delete reservation by id

---

