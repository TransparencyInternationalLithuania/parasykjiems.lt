CREATE INDEX "search_territory_upper_municipality" ON "search_territory" (upper(municipality));
CREATE INDEX "search_territory_upper_elderate" ON "search_territory" (upper(elderate));
CREATE INDEX "search_territory_upper_city" ON "search_territory" (upper(city));
CREATE INDEX "search_territory_upper_street" ON "search_territory" (upper(street));
