# Copyright 2018 Google LLC
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

"""This script is used to synthesize generated parts of this library."""

import re

import synthtool as s
from synthtool import gcp

gapic = gcp.GAPICBazel()
common = gcp.CommonTemplates()
versions = ["v1beta2", "v1"]

# ----------------------------------------------------------------------------
# Generate dataproc GAPIC layer
# ----------------------------------------------------------------------------
for version in versions:
    library = gapic.py_library(
        service="dataproc",
        version=version,
        bazel_target=f"//google/cloud/dataproc/{version}:dataproc-{version}-py",
        include_protos=True,
    )
    s.move(library, excludes=["docs/index.rst", "nox.py", "README.rst", "setup.py"])

    s.replace(
        f"google/cloud/dataproc_{version}/gapic/cluster_controller_client.py",
        "metadata_type=operations_pb2.ClusterOperationMetadata,",
        "metadata_type=proto_operations_pb2.ClusterOperationMetadata,",
    )

    s.replace(
        f"google/cloud/dataproc_{version}/gapic/cluster_controller_client.py",
        "\s+<strong>Note:</strong>.*\n(.*\n)+?.*types.FieldMask.",
        f"""


                .. note::

                    Currently, only the following fields can be updated:

                    * ``labels``: Update labels
                    * ``config.worker_config.num_instances``: Resize primary
                      worker group
                    * ``config.secondary_worker_config.num_instances``: Resize
                      secondary worker group

                    If a dict is provided, it must be of the same form as the protobuf
                    message :class:`~google.cloud.dataproc_{version}.types.FieldMask`""",
    )

    s.replace(
        f'google/cloud/dataproc_{version}/proto/workflow_templates_pb2.py',
        ', and must\n\s+conform to the following PCRE regular expression:'
        '(.*\n)+?.*No more than 32',
        '. Label values must be between\n'
        '          1 and 63 characters long. No more than 32'
    )
    s.replace(
        f'google/cloud/dataproc_{version}/proto/workflow_templates_pb2.py',
        ', and must conform to\n'
        '\s+the following regular expression:(.*\n)+?.* No more than',
        '. Label values must be between\n'
        '          1 and 63 characters long. No more than'
    )

s.replace(
    "google/cloud/dataproc_v1beta2/proto/clusters_pb2.py",
    "# Generated by the protocol buffer compiler.  DO NOT EDIT!",
    "# -*- coding: utf-8 -*-\n"
    "# Generated by the protocol buffer compiler.  DO NOT EDIT!",
)

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(unit_cov_level=97, cov_level=89)
s.move(templated_files)

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
