#cython: language_level=3
# Copyright 2016-2020 Google LLC
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
#

# See www.openfst.org for extensive documentation on this weighted
# finite-state transducer library.


from libc.stdint cimport *


cdef extern from "<fst/types.h>" nogil:

  ctypedef int8_t int8
  ctypedef int16_t int16
  ctypedef int32_t int32
  ctypedef int64_t int64
  ctypedef uint8_t uint8
  ctypedef uint16_t uint16
  ctypedef uint32_t uint32
  ctypedef uint64_t uint64

