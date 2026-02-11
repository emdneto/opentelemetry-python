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

import pytest

from opentelemetry.sdk.metrics import (
    AlwaysOffExemplarFilter,
    MeterProvider,
    TraceBasedExemplarFilter,
)
from opentelemetry.sdk.metrics.export import (
    InMemoryMetricReader,
)


@pytest.fixture
def meter_always_off():
    reader = InMemoryMetricReader()
    provider = MeterProvider(
        metric_readers=[reader],
        exemplar_filter=AlwaysOffExemplarFilter(),
    )
    return provider.get_meter("benchmark_always_off")


@pytest.fixture
def meter_trace_based():
    reader = InMemoryMetricReader()
    provider = MeterProvider(
        metric_readers=[reader],
        exemplar_filter=TraceBasedExemplarFilter(),
    )
    return provider.get_meter("benchmark_trace_based")


def test_counter_add_always_off(benchmark, meter_always_off):
    """Benchmark counter.add() with always_off exemplar filter (uses NoOpExemplarReservoir)"""
    counter = meter_always_off.create_counter("test_counter_always_off")
    labels = {"key": "value"}

    def counter_add():
        counter.add(1, labels)

    benchmark(counter_add)


def test_counter_add_trace_based(benchmark, meter_trace_based):
    """Benchmark counter.add() with trace_based exemplar filter"""
    counter = meter_trace_based.create_counter("test_counter_trace_based")
    labels = {"key": "value"}

    def counter_add():
        counter.add(1, labels)

    benchmark(counter_add)
