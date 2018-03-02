create table if not exists entries(
  id integer primary key autoincrement,
  name text not null,
  phone text not null,
  verification_code integer not null
);