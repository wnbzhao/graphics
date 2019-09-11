#Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for OpenGL math routines."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

from absl.testing import parameterized
import numpy as np
import tensorflow as tf

from tensorflow_graphics.rendering.opengl import math as glm
from tensorflow_graphics.util import test_case


class MathTest(test_case.TestCase):

  def test_perspective_right_handed_preset(self):
    """Tests that perspective_right_handed generates expected results.."""
    vertical_field_of_view = (60.0 * math.pi / 180.0, 50.0 * math.pi / 180.0)
    aspect_ratio = (1.5, 1.1)
    near = (1.0, 1.2)
    far = (10.0, 5.0)

    pred = glm.perspective_right_handed(vertical_field_of_view, aspect_ratio,
                                        near, far)
    gt = (((1.15470052, 0.0, 0.0, 0.0), (0.0, 1.73205066, 0.0, 0.0),
           (0.0, 0.0, -1.22222221, -2.22222233), (0.0, 0.0, -1.0, 0.0)),
          ((1.9495517, 0.0, 0.0, 0.0), (0.0, 2.14450693, 0.0, 0.0),
           (0.0, 0.0, -1.63157892, -3.15789485), (0.0, 0.0, -1.0, 0.0)))
    self.assertAllClose(pred, gt)

  @parameterized.parameters(
      ((1,), (1,), (1,), (1,)),
      ((None, 2), (None, 2), (None, 2), (None, 2)),
  )
  def test_perspective_right_handed_exception_not_raised(self, *shapes):
    """Tests that the shape exceptions are not raised."""
    self.assert_exception_is_not_raised(glm.perspective_right_handed, shapes)

  @parameterized.parameters(
      ("Not all batch dimensions are identical", (3,), (3, 3), (3, 3), (3, 3)),
      ("Not all batch dimensions are identical", (2, 3), (3, 3), (3, 3),
       (3, 3)),
  )
  def test_perspective_right_handed_shape_exception_raised(
      self, error_msg, *shapes):
    """Tests that the shape exceptions are properly raised."""
    self.assert_exception_is_raised(glm.perspective_right_handed, error_msg,
                                    shapes)

  @parameterized.parameters(
      ((1.0,),
       (1.0,), np.random.uniform(-1.0, 0.0, size=(1,)).astype(np.float32),
       (1.0,)),
      ((1.0,), (1.0,), (0.0,), (1.0,)),
      ((1.0,), np.random.uniform(-1.0, 0.0, size=(1,)).astype(np.float32),
       (0.1,), (1.0,)),
      ((1.0,), (0.0,), (0.1,), (1.0,)),
      ((1.0,),
       (1.0,), np.random.uniform(1.0, 2.0, size=(1,)).astype(np.float32),
       np.random.uniform(0.1, 0.5, size=(1,)).astype(np.float32)),
      ((1.0,), (1.0,), (0.1,), (0.1,)),
      (np.random.uniform(-math.pi, 0.0, size=(1,)).astype(np.float32), (1.0,),
       (0.1,), (1.0,)),
      (np.random.uniform(math.pi, 2.0 * math.pi, size=(1,)).astype(np.float32),
       (1.0,), (0.1,), (1.0,)),
      ((0.0,), (1.0,), (0.1,), (1.0,)),
      ((math.pi,), (1.0,), (0.1,), (1.0,)),
  )
  def test_perspective_right_handed_valid_range_exception_raised(
      self, vertical_field_of_view, aspect_ratio, near, far):
    """Tests that an exception is raised with out of bounds values."""
    with self.assertRaises(tf.errors.InvalidArgumentError):
      self.evaluate(
          glm.perspective_right_handed(vertical_field_of_view, aspect_ratio,
                                       near, far))

  def test_perspective_right_handed_cross_jacobian_preset(self):
    """Tests the Jacobian of perspective_right_handed."""
    vertical_field_of_view_init = np.array((1.0,))
    aspect_ratio_init = np.array((1.0,))
    near_init = np.array((1.0,))
    far_init = np.array((10.0,))

    # Wrap with tf.identity because some assert_* ops look at the constant
    # tensor value and mark it as unfeedable.
    vertical_field_of_view_tensor = tf.identity(
        tf.convert_to_tensor(value=vertical_field_of_view_init))
    aspect_ratio_tensor = tf.identity(
        tf.convert_to_tensor(value=aspect_ratio_init))
    near_tensor = tf.identity(tf.convert_to_tensor(value=near_init))
    far_tensor = tf.identity(tf.convert_to_tensor(value=far_init))

    y = glm.perspective_right_handed(vertical_field_of_view_tensor,
                                     aspect_ratio_tensor, near_tensor,
                                     far_tensor)

    self.assert_jacobian_is_correct(vertical_field_of_view_tensor,
                                    vertical_field_of_view_init, y)
    self.assert_jacobian_is_correct(aspect_ratio_tensor, aspect_ratio_init, y)
    self.assert_jacobian_is_correct(near_tensor, near_init, y)
    self.assert_jacobian_is_correct(far_tensor, far_init, y)

  def test_perspective_right_handed_cross_jacobian_random(self):
    """Tests the Jacobian of perspective_right_handed."""
    tensor_size = np.random.randint(1, 3)
    tensor_shape = np.random.randint(1, 5, size=(tensor_size)).tolist()
    eps = np.finfo(np.float64).eps
    vertical_field_of_view_init = np.random.uniform(
        eps, math.pi - eps, size=tensor_shape)
    aspect_ratio_init = np.random.uniform(eps, 100.0, size=tensor_shape)
    near_init = np.random.uniform(eps, 10.0, size=tensor_shape)
    far_init = np.random.uniform(10 + eps, 100.0, size=tensor_shape)

    # Wrap with tf.identity because some assert_* ops look at the constant
    # tensor value and mark it as unfeedable.
    vertical_field_of_view_tensor = tf.identity(
        tf.convert_to_tensor(value=vertical_field_of_view_init))
    aspect_ratio_tensor = tf.identity(
        tf.convert_to_tensor(value=aspect_ratio_init))
    near_tensor = tf.identity(tf.convert_to_tensor(value=near_init))
    far_tensor = tf.identity(tf.convert_to_tensor(value=far_init))

    y = glm.perspective_right_handed(vertical_field_of_view_tensor,
                                     aspect_ratio_tensor, near_tensor,
                                     far_tensor)

    self.assert_jacobian_is_correct(vertical_field_of_view_tensor,
                                    vertical_field_of_view_init, y)
    self.assert_jacobian_is_correct(aspect_ratio_tensor, aspect_ratio_init, y)
    self.assert_jacobian_is_correct(near_tensor, near_init, y)
    self.assert_jacobian_is_correct(far_tensor, far_init, y)


if __name__ == "__main__":
  test_case.main()
