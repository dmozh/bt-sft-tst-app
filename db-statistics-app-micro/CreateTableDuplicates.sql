CREATE TABLE public."duplicates" (
    id uuid,
    requestKey text,
    duplicates integer
);

ALTER TABLE IF EXISTS public."keybody"
    OWNER TO postgres;