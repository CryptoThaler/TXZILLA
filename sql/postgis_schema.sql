CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS real_estate;

CREATE TABLE IF NOT EXISTS real_estate.properties (
    property_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parcel_number TEXT NOT NULL,
    county TEXT NOT NULL,
    address_line1 TEXT,
    city TEXT,
    state CHAR(2) NOT NULL DEFAULT 'TX',
    postal_code TEXT,
    location GEOMETRY(Point, 4326) NOT NULL,
    parcel_geometry GEOMETRY(MultiPolygon, 4326),
    parcel_resolution_confidence NUMERIC(4, 3) NOT NULL DEFAULT 1.000,
    acreage NUMERIC(12, 4),
    zoning_code TEXT,
    land_use_code TEXT,
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    source_observed_at TIMESTAMPTZ NOT NULL,
    source_fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT properties_state_tx CHECK (state = 'TX'),
    CONSTRAINT properties_parcel_resolution_confidence_range
        CHECK (parcel_resolution_confidence >= 0 AND parcel_resolution_confidence <= 1),
    CONSTRAINT properties_acreage_non_negative CHECK (acreage IS NULL OR acreage >= 0),
    CONSTRAINT properties_unique_source_record UNIQUE (source_name, source_record_id),
    CONSTRAINT properties_unique_parcel UNIQUE (county, parcel_number)
);

CREATE INDEX IF NOT EXISTS properties_location_gix
    ON real_estate.properties
    USING GIST (location);

CREATE INDEX IF NOT EXISTS properties_parcel_geometry_gix
    ON real_estate.properties
    USING GIST (parcel_geometry);

CREATE INDEX IF NOT EXISTS properties_county_idx
    ON real_estate.properties (county);

CREATE TABLE IF NOT EXISTS real_estate.assessment_history (
    assessment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES real_estate.properties (property_id),
    tax_year INTEGER NOT NULL,
    assessed_total_value NUMERIC(14, 2) NOT NULL,
    assessed_land_value NUMERIC(14, 2),
    assessed_improvement_value NUMERIC(14, 2),
    taxable_value NUMERIC(14, 2),
    tax_amount_annual NUMERIC(14, 2),
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    source_observed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT assessment_history_total_non_negative CHECK (assessed_total_value >= 0),
    CONSTRAINT assessment_history_unique_slice
        UNIQUE (property_id, tax_year, source_name, source_record_id)
);

CREATE INDEX IF NOT EXISTS assessment_history_property_id_idx
    ON real_estate.assessment_history (property_id, tax_year DESC);

CREATE TABLE IF NOT EXISTS real_estate.ownership_history (
    ownership_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES real_estate.properties (property_id),
    owner_name TEXT NOT NULL,
    ownership_start_date DATE,
    ownership_end_date DATE,
    mailing_address TEXT,
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    source_observed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ownership_history_unique_slice
        UNIQUE (property_id, owner_name, source_name, source_record_id, source_observed_at)
);

CREATE INDEX IF NOT EXISTS ownership_history_property_id_idx
    ON real_estate.ownership_history (property_id, source_observed_at DESC);

CREATE TABLE IF NOT EXISTS real_estate.listings (
    listing_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES real_estate.properties (property_id),
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    listing_status TEXT NOT NULL,
    list_price NUMERIC(14, 2) NOT NULL,
    listed_at DATE,
    removed_at DATE,
    days_on_market INTEGER,
    bedrooms NUMERIC(4, 1),
    bathrooms NUMERIC(4, 1),
    building_area_sqft NUMERIC(12, 2),
    lot_size_acres NUMERIC(12, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT listings_list_price_positive CHECK (list_price > 0),
    CONSTRAINT listings_days_on_market_non_negative
        CHECK (days_on_market IS NULL OR days_on_market >= 0),
    CONSTRAINT listings_source_record_unique UNIQUE (source_name, source_record_id)
);

CREATE INDEX IF NOT EXISTS listings_property_id_idx
    ON real_estate.listings (property_id);

CREATE INDEX IF NOT EXISTS listings_status_idx
    ON real_estate.listings (listing_status);

CREATE TABLE IF NOT EXISTS real_estate.transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES real_estate.properties (property_id),
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    recorded_date DATE NOT NULL,
    sale_price NUMERIC(14, 2),
    document_number TEXT,
    buyer_name TEXT,
    seller_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT transactions_sale_price_positive
        CHECK (sale_price IS NULL OR sale_price > 0),
    CONSTRAINT transactions_source_record_unique UNIQUE (source_name, source_record_id)
);

CREATE INDEX IF NOT EXISTS transactions_property_id_idx
    ON real_estate.transactions (property_id);

CREATE INDEX IF NOT EXISTS transactions_recorded_date_idx
    ON real_estate.transactions (recorded_date);

CREATE TABLE IF NOT EXISTS real_estate.rental_market (
    rental_market_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_key TEXT NOT NULL,
    effective_date DATE NOT NULL,
    property_type TEXT NOT NULL,
    bedroom_count INTEGER,
    median_rent NUMERIC(12, 2) NOT NULL,
    rent_per_sqft NUMERIC(10, 4),
    vacancy_rate NUMERIC(6, 4),
    growth_yoy NUMERIC(6, 4),
    confidence NUMERIC(4, 3) NOT NULL DEFAULT 1.000,
    market_geometry GEOMETRY(MultiPolygon, 4326),
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT rental_market_median_rent_non_negative CHECK (median_rent >= 0),
    CONSTRAINT rental_market_vacancy_rate_range
        CHECK (vacancy_rate IS NULL OR (vacancy_rate >= 0 AND vacancy_rate <= 1)),
    CONSTRAINT rental_market_confidence_range CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT rental_market_source_record_unique UNIQUE (source_name, source_record_id),
    CONSTRAINT rental_market_effective_slice_unique
        UNIQUE (region_key, effective_date, property_type, bedroom_count)
);

CREATE INDEX IF NOT EXISTS rental_market_region_idx
    ON real_estate.rental_market (region_key, effective_date);

CREATE INDEX IF NOT EXISTS rental_market_geometry_gix
    ON real_estate.rental_market
    USING GIST (market_geometry);

CREATE TABLE IF NOT EXISTS real_estate.environmental_risk (
    environmental_risk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES real_estate.properties (property_id),
    risk_layer TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    risk_score NUMERIC(6, 2) NOT NULL,
    effective_date DATE NOT NULL,
    risk_geometry GEOMETRY(MultiPolygon, 4326) NOT NULL,
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    provenance JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT environmental_risk_score_range CHECK (risk_score >= 0 AND risk_score <= 100),
    CONSTRAINT environmental_risk_source_record_unique UNIQUE (source_name, source_record_id)
);

CREATE INDEX IF NOT EXISTS environmental_risk_property_id_idx
    ON real_estate.environmental_risk (property_id);

CREATE INDEX IF NOT EXISTS environmental_risk_geometry_gix
    ON real_estate.environmental_risk
    USING GIST (risk_geometry);

CREATE TABLE IF NOT EXISTS real_estate.market_features (
    market_feature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_key TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    feature_value NUMERIC(14, 4) NOT NULL,
    value_unit TEXT,
    effective_date DATE NOT NULL,
    feature_geometry GEOMETRY(MultiPolygon, 4326),
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT market_features_source_record_unique UNIQUE (source_name, source_record_id),
    CONSTRAINT market_features_effective_slice_unique
        UNIQUE (region_key, feature_name, effective_date, source_name)
);

CREATE INDEX IF NOT EXISTS market_features_region_idx
    ON real_estate.market_features (region_key, effective_date);

CREATE INDEX IF NOT EXISTS market_features_geometry_gix
    ON real_estate.market_features
    USING GIST (feature_geometry);

CREATE TABLE IF NOT EXISTS real_estate.investment_scores (
    investment_score_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES real_estate.properties (property_id),
    effective_date DATE NOT NULL,
    formula_version TEXT NOT NULL,
    acquisition_basis NUMERIC(14, 2) NOT NULL,
    estimated_rent NUMERIC(12, 2) NOT NULL,
    monthly_cash_flow NUMERIC(14, 2) NOT NULL,
    annual_noi NUMERIC(14, 2) NOT NULL,
    cap_rate NUMERIC(10, 6) NOT NULL,
    cash_flow_score NUMERIC(6, 2) NOT NULL,
    appreciation_score NUMERIC(6, 2) NOT NULL,
    market_growth_score NUMERIC(6, 2) NOT NULL,
    risk_inverse_score NUMERIC(6, 2) NOT NULL,
    liquidity_score NUMERIC(6, 2) NOT NULL,
    investment_score NUMERIC(6, 2) NOT NULL,
    assumptions JSONB NOT NULL DEFAULT '[]'::jsonb,
    weights JSONB NOT NULL DEFAULT
        '{"cash_flow": 0.30, "appreciation": 0.25, "market_growth": 0.20, "risk_inverse": 0.15, "liquidity": 0.10}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT investment_scores_acquisition_basis_positive CHECK (acquisition_basis > 0),
    CONSTRAINT investment_scores_estimated_rent_non_negative CHECK (estimated_rent >= 0),
    CONSTRAINT investment_scores_cash_flow_score_range
        CHECK (cash_flow_score >= 0 AND cash_flow_score <= 100),
    CONSTRAINT investment_scores_appreciation_score_range
        CHECK (appreciation_score >= 0 AND appreciation_score <= 100),
    CONSTRAINT investment_scores_market_growth_score_range
        CHECK (market_growth_score >= 0 AND market_growth_score <= 100),
    CONSTRAINT investment_scores_risk_inverse_score_range
        CHECK (risk_inverse_score >= 0 AND risk_inverse_score <= 100),
    CONSTRAINT investment_scores_liquidity_score_range
        CHECK (liquidity_score >= 0 AND liquidity_score <= 100),
    CONSTRAINT investment_scores_investment_score_range
        CHECK (investment_score >= 0 AND investment_score <= 100),
    CONSTRAINT investment_scores_unique_version
        UNIQUE (property_id, effective_date, formula_version)
);

CREATE INDEX IF NOT EXISTS investment_scores_property_id_idx
    ON real_estate.investment_scores (property_id, effective_date);

CREATE TABLE IF NOT EXISTS real_estate.land_ag_features (
    land_ag_feature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES real_estate.properties (property_id),
    feature_name TEXT NOT NULL,
    feature_value NUMERIC(14, 4),
    value_unit TEXT,
    effective_date DATE NOT NULL,
    feature_geometry GEOMETRY(MultiPolygon, 4326),
    source_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT land_ag_features_source_record_unique UNIQUE (source_name, source_record_id)
);

CREATE INDEX IF NOT EXISTS land_ag_features_property_id_idx
    ON real_estate.land_ag_features (property_id, effective_date);

CREATE INDEX IF NOT EXISTS land_ag_features_geometry_gix
    ON real_estate.land_ag_features
    USING GIST (feature_geometry);

CREATE TABLE IF NOT EXISTS real_estate.provider_runs (
    provider_run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_name TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    region_key TEXT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fetched_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    run_status TEXT NOT NULL,
    record_count INTEGER NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT provider_runs_record_count_non_negative CHECK (record_count >= 0)
);

CREATE INDEX IF NOT EXISTS provider_runs_provider_idx
    ON real_estate.provider_runs (provider_name, fetched_at DESC);

CREATE TABLE IF NOT EXISTS real_estate.raw_properties (
    raw_property_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_run_id UUID NOT NULL REFERENCES real_estate.provider_runs (provider_run_id),
    provider_name TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    county TEXT,
    region_key TEXT,
    fetched_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL,
    standardized_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT raw_properties_unique_source_record
        UNIQUE (provider_name, source_record_id, fetched_at)
);

CREATE INDEX IF NOT EXISTS raw_properties_run_idx
    ON real_estate.raw_properties (provider_run_id);

CREATE TABLE IF NOT EXISTS real_estate.raw_listings (
    raw_listing_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_run_id UUID NOT NULL REFERENCES real_estate.provider_runs (provider_run_id),
    provider_name TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    county TEXT,
    region_key TEXT,
    fetched_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL,
    standardized_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT raw_listings_unique_source_record
        UNIQUE (provider_name, source_record_id, fetched_at)
);

CREATE INDEX IF NOT EXISTS raw_listings_run_idx
    ON real_estate.raw_listings (provider_run_id);

CREATE TABLE IF NOT EXISTS real_estate.entity_resolution_events (
    entity_resolution_event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_run_id UUID NOT NULL REFERENCES real_estate.provider_runs (provider_run_id),
    provider_name TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    canonical_entity_type TEXT NOT NULL,
    canonical_entity_id UUID,
    match_status TEXT NOT NULL,
    confidence NUMERIC(4, 3) NOT NULL,
    resolution_reason TEXT NOT NULL,
    event_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT entity_resolution_events_confidence_range
        CHECK (confidence >= 0 AND confidence <= 1)
);

CREATE INDEX IF NOT EXISTS entity_resolution_events_run_idx
    ON real_estate.entity_resolution_events (provider_run_id);

CREATE TABLE IF NOT EXISTS real_estate.provider_run_artifacts (
    provider_run_artifact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_run_id UUID NOT NULL REFERENCES real_estate.provider_runs (provider_run_id),
    county TEXT,
    dataset_key TEXT NOT NULL,
    source_url TEXT NOT NULL,
    local_path TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    media_type TEXT,
    bytes_downloaded BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT provider_run_artifacts_bytes_non_negative CHECK (bytes_downloaded >= 0)
);

CREATE INDEX IF NOT EXISTS provider_run_artifacts_run_idx
    ON real_estate.provider_run_artifacts (provider_run_id);
