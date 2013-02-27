DROP VIEW Vkolcs_view;
DROP TABLE Video;

CREATE TABLE Video (
	sz integer NOT NULL,
	cim text DEFAULT '',
	szerzo text DEFAULT '',
	rendezo text DEFAULT '',
	orszag text DEFAULT '',
	mufaj text DEFAULT '',
	tema text DEFAULT '',
	ido time WITHOUT TIME ZONE,
	megj text DEFAULT '',
	tele text DEFAULT '',
	nyelv text DEFAULT '',
	dvd text DEFAULT ''
);

REVOKE ALL ON Video FROM PUBLIC;
GRANT SELECT ON Video TO PUBLIC;


CREATE VIEW Vkolcs_view AS
	SELECT DISTINCT X.id, V.sz, E.tip, E.esz, E.enev, X.ki
	FROM ember AS E, vkolcs AS X, video AS V
	WHERE X.be IS NULL AND (E.tip)::text = X.tip AND E.esz = X.esz AND X.sz = V.sz
		ORDER BY X.id, V.sz, E.tip, E.esz, E.enev, X.ki;

REVOKE ALL ON Vkolcs_view FROM PUBLIC;
GRANT SELECT ON Vkolcs_view TO jutka;


