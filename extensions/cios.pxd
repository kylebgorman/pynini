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


from libcpp.string cimport string

from cintegral_types cimport int8
from cintegral_types cimport int16
from cintegral_types cimport int32
from cintegral_types cimport int64
from cintegral_types cimport uint8
from cintegral_types cimport uint16
from cintegral_types cimport uint32
from cintegral_types cimport uint64


cdef extern from "<iostream>" namespace "std" nogil:

  cdef cppclass iostream:

    pass

  cdef cppclass istream(iostream):

    pass

  cdef cppclass ostream(iostream):

    pass


# We are ignoring openmodes for the moment.


cdef extern from "<fstream>" namespace "std" nogil:

  cdef cppclass ifstream(istream):

    ifstream(const string &)

  cdef cppclass ofstream(ostream):

    ofstream(const string &)


cdef extern from "<sstream>" namespace "std" nogil:

  cdef cppclass stringstream(istream, ostream):

    stringstream()

    string str()

    stringstream &operator<<(const string &)

    stringstream &operator<<(bool)

    # We define these in terms of the Google cintegral_types.

    stringstream &operator<<(int8)

    stringstream &operator<<(uint8)

    stringstream &operator<<(int16)

    stringstream &operator<<(uint16)

    stringstream &operator<<(int32)

    stringstream &operator<<(uint32)

    stringstream &operator<<(int64)

    stringstream &operator<<(uint64)

    stringstream &operator<<(double)

    stringstream &operator<<(long double)

