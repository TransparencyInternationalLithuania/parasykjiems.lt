CREATE INDEX "search_location_upper_municipality" ON "search_location" (upper(municipality));
CREATE INDEX "search_location_upper_elderate" ON "search_location" (upper(elderate));
CREATE INDEX "search_location_upper_city" ON "search_location" (upper(city));
CREATE INDEX "search_location_upper_street" ON "search_location" (upper(street));
