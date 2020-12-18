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


#TODO(kbg): When/if PR https://github.com/cython/cython/pull/3358 is merged
# and we update third-party Cython up to or beyond a version that includes
# this, delete this file and instead use libcpp.utility.move.
cdef extern from * namespace "fst":
    """
    #include <type_traits>
    #include <utility>

    namespace fst {

    template <typename T>
    inline typename std::remove_reference<T>::type &&move(T &t) {
        return std::move(t);
    }

    template <typename T>
    inline typename std::remove_reference<T>::type &&move(T &&t) {
        return std::move(t);
    }

    }  // namespace fst
    """
    cdef T move[T](T)

