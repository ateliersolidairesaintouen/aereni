# Database

## Aereni

```sql
CREATE DATABASE aereni;
```

Tables

```sql
CREATE TABLE Users
(id SERIAL PRIMARY KEY,
name character varying(255),
fname character varying(255),
pass character varying(255),
mail character varying(255),
phone character varying(255),
address character varying(255));
```

```sql
INSERT INTO Users(name, fname, pass, mail, phone, address)
VALUES ("Simpson", "Homer", "Donuts", "homer@simps.on", "+9942", "742 Evergreen Terrace Springfield, États-Unis");
```

```sql
CREATE TABLE Status
(id SERIAL PRIMARY KEY,
name character varying(255),
```
```sql
INSERT INTO Status(name)
VALUES 
  ("Prod"),
  ("H.S."),
  ("Standby");
```

```sql
CREATE TABLE Exposure
(id SERIAL PRIMARY KEY,
name character varying(255),
```
```sql
INSERT INTO Exposure(name)
VALUES 
  ("Outdoor"),
  ("Indoor");
```

```sql
CREATE TABLE Sensors
(id INTEGER PRIMARY KEY,
name character varying(255),
status_id character varying(255),
user_id integer,
owner_id integer,
gps point,
height integer,
exposure_id character varying(255)
);
```

```sql
INSERT INTO Sensors(id, name, status, user_id, owner_id, gps, height, exposure)
VALUES ("424242", "Atelier Solidaire", "1", "1", "1", "(x, y"), "3.5", "1";
```
