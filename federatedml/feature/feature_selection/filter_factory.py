#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from arch.api.utils import log_utils
from federatedml.feature.feature_selection.iso_model_filter import IsoModelFilter, FederatedIsoModelFilter
from federatedml.feature.feature_selection.manually_filter import ManuallyFilter
from federatedml.feature.feature_selection.percentage_value_filter import PercentageValueFilter
from federatedml.feature.feature_selection.unique_value_filter import UniqueValueFilter
from federatedml.param import feature_selection_param
from federatedml.param.feature_selection_param import FeatureSelectionParam
from federatedml.util import consts

LOGGER = log_utils.getLogger()


def get_filter(filter_name, model_param: FeatureSelectionParam, role=consts.GUEST, model=None):
    LOGGER.debug(f"Getting filter name: {filter_name}")

    if filter_name == consts.UNIQUE_VALUE:
        unique_param = model_param.unique_param
        return UniqueValueFilter(unique_param)

    elif filter_name == consts.IV_VALUE_THRES:
        iv_value_param = model_param.iv_value_param
        iv_param = feature_selection_param.CommonFilterParam(
            metrics=consts.IV,
            filter_type='threshold',
            take_high=True,
            threshold=iv_value_param.value_threshold,
            host_thresholds=iv_value_param.host_thresholds,
            select_federated=not iv_value_param.local_only
        )
        iv_param.check()
        iso_model = model.isometric_models.get(consts.BINNING_MODEL)
        if iso_model is None:
            raise ValueError("None of binning model has provided when using iv filter")
        return FederatedIsoModelFilter(iv_param, iso_model,
                                       role=role, cpp=model.component_properties)

    elif filter_name == consts.IV_PERCENTILE:
        iv_percentile_param = model_param.iv_percentile_param
        iv_param = feature_selection_param.CommonFilterParam(
            metrics=consts.IV,
            filter_type='top_percentile',
            take_high=True,
            threshold=iv_percentile_param.percentile_threshold,
            select_federated=not iv_percentile_param.local_only
        )
        iv_param.check()
        iso_model = model.isometric_models.get(consts.BINNING_MODEL)
        if iso_model is None:
            raise ValueError("None of binning model has provided when using iv filter")
        return FederatedIsoModelFilter(iv_param, iso_model,
                                       role=role, cpp=model.component_properties)

    elif filter_name == consts.IV_TOP_K:
        iv_top_k_param = model_param.iv_top_k_param
        iv_param = feature_selection_param.CommonFilterParam(
            metrics=consts.IV,
            filter_type='top_k',
            take_high=True,
            threshold=iv_top_k_param.k,
            select_federated=not iv_top_k_param.local_only
        )
        iv_param.check()
        iso_model = model.isometric_models.get(consts.BINNING_MODEL)
        if iso_model is None:
            raise ValueError("None of binning model has provided when using iv filter")
        return FederatedIsoModelFilter(iv_param, iso_model,
                                       role=role, cpp=model.component_properties)

    elif filter_name == consts.COEFFICIENT_OF_VARIATION_VALUE_THRES:
        variance_coe_param = model_param.variance_coe_param
        coe_param = feature_selection_param.CommonFilterParam(
            metrics=consts.COEFFICIENT_OF_VARIATION,
            filter_type='threshold',
            take_high=True,
            threshold=variance_coe_param.value_threshold
        )
        coe_param.check()
        iso_model = model.isometric_models.get(consts.STATISTIC_MODEL)
        if iso_model is None:
            raise ValueError("None of statistic model has provided when using iv filter")
        return IsoModelFilter(coe_param, iso_model)


    elif filter_name == consts.OUTLIER_COLS:
        outlier_param = model_param.outlier_param
        new_param = feature_selection_param.CommonFilterParam(
            metrics=str(int(outlier_param.percentile * 100)) + "%",
            filter_type='threshold',
            take_high=False,
            threshold=outlier_param.upper_threshold
        )
        new_param.check()
        iso_model = model.isometric_models.get(consts.STATISTIC_MODEL)
        if iso_model is None:
            raise ValueError("None of statistic model has provided when using iv filter")
        return IsoModelFilter(new_param, iso_model)

        # outlier_param = model_param.outlier_param
        # return OutlierFilter(outlier_param)

    elif filter_name == consts.MANUALLY_FILTER:
        manually_param = model_param.manually_param
        return ManuallyFilter(manually_param)

    elif filter_name == consts.PERCENTAGE_VALUE:
        percentage_value_param = model_param.percentage_value_param
        return PercentageValueFilter(percentage_value_param)

    else:
        raise ValueError("filter method: {} does not exist".format(filter_name))
