# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from time import time_ns
from unittest import TestCase, mock
from unittest.mock import MagicMock

from opentelemetry.context import Context
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal._view_instrument_match import (
    _noop_reservoir_factory,
    _ViewInstrumentMatch,
)
from opentelemetry.sdk.metrics._internal.aggregation import (
    _ExplicitBucketHistogramAggregation,
    _SumAggregation,
)
from opentelemetry.sdk.metrics._internal.exemplar import (
    AlwaysOffExemplarFilter,
    NoOpExemplarReservoir,
    TraceBasedExemplarFilter,
)
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.metrics.view import DefaultAggregation, View


class TestNoOpExemplarReservoir(TestCase):
    def test_offer_does_nothing(self):
        reservoir = NoOpExemplarReservoir()
        reservoir.offer(42.0, time_ns(), {"key": "value"}, Context())

    def test_collect_returns_empty_list(self):
        reservoir = NoOpExemplarReservoir()
        reservoir.offer(1.0, time_ns(), {"key": "value"}, Context())
        exemplars = reservoir.collect({"key": "value"})
        self.assertEqual(exemplars, [])

    def test_noop_exemplar_reservoir_kwargs(self):
        reservoir = NoOpExemplarReservoir(size=10, boundaries=[0, 5, 10])
        self.assertIsInstance(reservoir, NoOpExemplarReservoir)

    def test_collect_always_empty_after_multiple_offers(self):
        reservoir = NoOpExemplarReservoir()
        for i in range(100):
            reservoir.offer(float(i), time_ns(), {"i": str(i)}, Context())
        self.assertEqual(reservoir.collect({}), [])


class TestNoOpReservoirWithAlwaysOffFilter(TestCase):
    def test_view_instrument_match_uses_noop_with_always_off_filter(self):
        instrument = MagicMock(name="test_instrument")
        instrument.instrumentation_scope = MagicMock()

        vim = _ViewInstrumentMatch(
            view=View(instrument_name="test_instrument"),
            instrument=instrument,
            instrument_class_aggregation=MagicMock(
                **{"__getitem__.return_value": DefaultAggregation()}
            ),
            exemplar_filter=AlwaysOffExemplarFilter(),
        )

        self.assertIs(vim._exemplar_reservoir_factory, _noop_reservoir_factory)

    def test_view_instrument_match_uses_default_without_always_off(self):
        instrument = MagicMock(name="test_instrument")
        instrument.instrumentation_scope = MagicMock()

        view = View(instrument_name="test_instrument")
        vim = _ViewInstrumentMatch(
            view=view,
            instrument=instrument,
            instrument_class_aggregation=MagicMock(
                **{"__getitem__.return_value": DefaultAggregation()}
            ),
            exemplar_filter=TraceBasedExemplarFilter(),
        )

        self.assertIs(
            vim._exemplar_reservoir_factory,
            view._exemplar_reservoir_factory,
        )

    def test_noop_reservoir_factory_returns_noop(self):
        self.assertIs(
            _noop_reservoir_factory(_SumAggregation),
            NoOpExemplarReservoir,
        )
        self.assertIs(
            _noop_reservoir_factory(_ExplicitBucketHistogramAggregation),
            NoOpExemplarReservoir,
        )

    def test_meter_provider_always_off_programmatic(self):
        reader = InMemoryMetricReader()
        provider = MeterProvider(
            metric_readers=[reader],
            exemplar_filter=AlwaysOffExemplarFilter(),
        )
        meter = provider.get_meter("test")
        counter = meter.create_counter("test_counter")
        counter.add(10, {"key": "value"})

        data = reader.get_metrics_data()
        metrics = data.resource_metrics[0].scope_metrics[0].metrics
        data_point = metrics[0].data.data_points[0]
        self.assertEqual(data_point.exemplars, [])

    @mock.patch.dict(
        os.environ, {"OTEL_METRICS_EXEMPLAR_FILTER": "always_off"}
    )
    def test_meter_provider_always_off_env_var(self):
        reader = InMemoryMetricReader()
        provider = MeterProvider(metric_readers=[reader])
        meter = provider.get_meter("test")
        counter = meter.create_counter("test_counter")
        counter.add(10, {"key": "value"})

        data = reader.get_metrics_data()
        metrics = data.resource_metrics[0].scope_metrics[0].metrics
        data_point = metrics[0].data.data_points[0]
        self.assertEqual(data_point.exemplars, [])
