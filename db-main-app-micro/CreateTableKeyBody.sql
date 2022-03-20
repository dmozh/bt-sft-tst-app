CREATE TABLE public."keybody" (
    id uuid,
    requestKey text,
    requestBody text,
    duplicates integer
);

ALTER TABLE IF EXISTS public."keybody"
    OWNER TO postgres;