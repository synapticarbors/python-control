#!/usr/bin/env python
#
# statesp_test.py - test state space class
# RMM, 30 Mar 2011 (based on TestStateSp from v0.4a)

import unittest
import numpy as np
from numpy.linalg import solve
from scipy.linalg import eigvals, block_diag
from control import matlab
from control.statesp import StateSpace, _convertToStateSpace
from control.xferfcn import TransferFunction
from control.exception import slycot_check

class TestStateSpace(unittest.TestCase):
    """Tests for the StateSpace class."""

    def setUp(self):
        """Set up a MIMO system to test operations on."""

        A = [[-3., 4., 2.], [-1., -3., 0.], [2., 5., 3.]]
        B = [[1., 4.], [-3., -3.], [-2., 1.]]
        C = [[4., 2., -3.], [1., 4., 3.]]
        D = [[-2., 4.], [0., 1.]]

        a = [[4., 1.], [2., -3]]
        b = [[5., 2.], [-3., -3.]]
        c = [[2., -4], [0., 1.]]
        d = [[3., 2.], [1., -1.]]

        self.sys1 = StateSpace(A, B, C, D)
        self.sys2 = StateSpace(a, b, c, d)

    def testPole(self):
        """Evaluate the poles of a MIMO system."""

        p = np.sort(self.sys1.pole())
        true_p = np.sort([3.34747678408874,
            -3.17373839204437 + 1.47492908003839j,
            -3.17373839204437 - 1.47492908003839j])

        np.testing.assert_array_almost_equal(p, true_p)

    def testZero(self):
        """Evaluate the zeros of a SISO system."""

        sys = StateSpace(self.sys1.A, [[3.], [-2.], [4.]], [[-1., 3., 2.]], [[-4.]])
        z = sys.zero()

        np.testing.assert_array_almost_equal(z, [4.26864638637134,
            -3.75932319318567 + 1.10087776649554j,
            -3.75932319318567 - 1.10087776649554j])

    def testAdd(self):
        """Add two MIMO systems."""

        A = [[-3., 4., 2., 0., 0.], [-1., -3., 0., 0., 0.],
             [2., 5., 3., 0., 0.], [0., 0., 0., 4., 1.], [0., 0., 0., 2., -3.]]
        B = [[1., 4.], [-3., -3.], [-2., 1.], [5., 2.], [-3., -3.]]
        C = [[4., 2., -3., 2., -4.], [1., 4., 3., 0., 1.]]
        D = [[1., 6.], [1., 0.]]

        sys = self.sys1 + self.sys2

        np.testing.assert_array_almost_equal(sys.A, A)
        np.testing.assert_array_almost_equal(sys.B, B)
        np.testing.assert_array_almost_equal(sys.C, C)
        np.testing.assert_array_almost_equal(sys.D, D)

    def testSub(self):
        """Subtract two MIMO systems."""

        A = [[-3., 4., 2., 0., 0.], [-1., -3., 0., 0., 0.],
             [2., 5., 3., 0., 0.], [0., 0., 0., 4., 1.], [0., 0., 0., 2., -3.]]
        B = [[1., 4.], [-3., -3.], [-2., 1.], [5., 2.], [-3., -3.]]
        C = [[4., 2., -3., -2., 4.], [1., 4., 3., 0., -1.]]
        D = [[-5., 2.], [-1., 2.]]

        sys = self.sys1 - self.sys2

        np.testing.assert_array_almost_equal(sys.A, A)
        np.testing.assert_array_almost_equal(sys.B, B)
        np.testing.assert_array_almost_equal(sys.C, C)
        np.testing.assert_array_almost_equal(sys.D, D)

    def testMul(self):
        """Multiply two MIMO systems."""

        A = [[4., 1., 0., 0., 0.], [2., -3., 0., 0., 0.], [2., 0., -3., 4., 2.],
             [-6., 9., -1., -3., 0.], [-4., 9., 2., 5., 3.]]
        B = [[5., 2.], [-3., -3.], [7., -2.], [-12., -3.], [-5., -5.]]
        C = [[-4., 12., 4., 2., -3.], [0., 1., 1., 4., 3.]]
        D = [[-2., -8.], [1., -1.]]

        sys = self.sys1 * self.sys2

        np.testing.assert_array_almost_equal(sys.A, A)
        np.testing.assert_array_almost_equal(sys.B, B)
        np.testing.assert_array_almost_equal(sys.C, C)
        np.testing.assert_array_almost_equal(sys.D, D)

    def testEvalFr(self):
        """Evaluate the frequency response at one frequency."""

        A = [[-2, 0.5], [0.5, -0.3]]
        B = [[0.3, -1.3], [0.1, 0.]]
        C = [[0., 0.1], [-0.3, -0.2]]
        D = [[0., -0.8], [-0.3, 0.]]
        sys = StateSpace(A, B, C, D)

        resp = [[4.37636761487965e-05 - 0.0152297592997812j,
                 -0.792603938730853 + 0.0261706783369803j],
                [-0.331544857768052 + 0.0576105032822757j,
                 0.128919037199125 - 0.143824945295405j]]

        np.testing.assert_almost_equal(sys.evalfr(1.), resp)

    @unittest.skipIf(not slycot_check(), "slycot not installed")
    def testFreqResp(self):
        """Evaluate the frequency response at multiple frequencies."""

        A = [[-2, 0.5], [0.5, -0.3]]
        B = [[0.3, -1.3], [0.1, 0.]]
        C = [[0., 0.1], [-0.3, -0.2]]
        D = [[0., -0.8], [-0.3, 0.]]
        sys = StateSpace(A, B, C, D)

        truemag = [[[0.0852992637230322, 0.00103596611395218],
                    [0.935374692849736, 0.799380720864549]],
                   [[0.55656854563842, 0.301542699860857],
                    [0.609178071542849, 0.0382108097985257]]]
        truephase = [[[-0.566195599644593, -1.68063565332582],
                      [3.0465958317514, 3.14141384339534]],
                     [[2.90457947657161, 3.10601268291914],
                      [-0.438157380501337, -1.40720969147217]]]
        trueomega = [0.1, 10.]

        mag, phase, omega = sys.freqresp(trueomega)

        np.testing.assert_almost_equal(mag, truemag)
        np.testing.assert_almost_equal(phase, truephase)
        np.testing.assert_equal(omega, trueomega)

    @unittest.skipIf(not slycot_check(), "slycot not installed")
    def testMinreal(self):
        """Test a minreal model reduction"""
        #A = [-2, 0.5, 0; 0.5, -0.3, 0; 0, 0, -0.1]
        A = [[-2, 0.5, 0], [0.5, -0.3, 0], [0, 0, -0.1]]
        #B = [0.3, -1.3; 0.1, 0; 1, 0]
        B = [[0.3, -1.3], [0.1, 0.], [1.0, 0.0]]
        #C = [0, 0.1, 0; -0.3, -0.2, 0]
        C = [[0., 0.1, 0.0], [-0.3, -0.2, 0.0]]
        #D = [0 -0.8; -0.3 0]
        D = [[0., -0.8], [-0.3, 0.]]
        # sys = ss(A, B, C, D)

        sys = StateSpace(A, B, C, D)
        sysr = sys.minreal()
        self.assertEqual(sysr.states, 2)
        self.assertEqual(sysr.inputs, sys.inputs)
        self.assertEqual(sysr.outputs, sys.outputs)
        np.testing.assert_array_almost_equal(
            eigvals(sysr.A), [-2.136154, -0.1638459])

    def testAppendSS(self):
        """Test appending two state-space systems"""
        A1 = [[-2, 0.5, 0], [0.5, -0.3, 0], [0, 0, -0.1]]
        B1 = [[0.3, -1.3], [0.1, 0.], [1.0, 0.0]]
        C1 = [[0., 0.1, 0.0], [-0.3, -0.2, 0.0]]
        D1 = [[0., -0.8], [-0.3, 0.]]
        A2 = [[-1.]]
        B2 = [[1.2]]
        C2 = [[0.5]]
        D2 = [[0.4]]
        A3 = [[-2, 0.5, 0, 0], [0.5, -0.3, 0, 0], [0, 0, -0.1, 0],
              [0, 0, 0., -1.]]
        B3 = [[0.3, -1.3, 0], [0.1, 0., 0], [1.0, 0.0, 0], [0., 0, 1.2]]
        C3 = [[0., 0.1, 0.0, 0.0], [-0.3, -0.2, 0.0, 0.0], [0., 0., 0., 0.5]]
        D3 = [[0., -0.8, 0.], [-0.3, 0., 0.], [0., 0., 0.4]]
        sys1 = StateSpace(A1, B1, C1, D1)
        sys2 = StateSpace(A2, B2, C2, D2)
        sys3 = StateSpace(A3, B3, C3, D3)
        sys3c = sys1.append(sys2)
        np.testing.assert_array_almost_equal(sys3.A, sys3c.A)
        np.testing.assert_array_almost_equal(sys3.B, sys3c.B)
        np.testing.assert_array_almost_equal(sys3.C, sys3c.C)
        np.testing.assert_array_almost_equal(sys3.D, sys3c.D)

    def testAppendTF(self):
        """Test appending a state-space system with a tf"""
        A1 = [[-2, 0.5, 0], [0.5, -0.3, 0], [0, 0, -0.1]]
        B1 = [[0.3, -1.3], [0.1, 0.], [1.0, 0.0]]
        C1 = [[0., 0.1, 0.0], [-0.3, -0.2, 0.0]]
        D1 = [[0., -0.8], [-0.3, 0.]]
        s = TransferFunction([1, 0], [1])
        h = 1/(s+1)/(s+2)
        sys1 = StateSpace(A1, B1, C1, D1)
        sys2 = _convertToStateSpace(h)
        sys3c = sys1.append(sys2)
        np.testing.assert_array_almost_equal(sys1.A, sys3c.A[:3,:3])
        np.testing.assert_array_almost_equal(sys1.B, sys3c.B[:3,:2])
        np.testing.assert_array_almost_equal(sys1.C, sys3c.C[:2,:3])
        np.testing.assert_array_almost_equal(sys1.D, sys3c.D[:2,:2])
        np.testing.assert_array_almost_equal(sys2.A, sys3c.A[3:,3:])
        np.testing.assert_array_almost_equal(sys2.B, sys3c.B[3:,2:])
        np.testing.assert_array_almost_equal(sys2.C, sys3c.C[2:,3:])
        np.testing.assert_array_almost_equal(sys2.D, sys3c.D[2:,2:])
        np.testing.assert_array_almost_equal(sys3c.A[:3,3:], np.zeros( (3, 2)) )
        np.testing.assert_array_almost_equal(sys3c.A[3:,:3], np.zeros( (2, 3)) )


    def testArrayAccessSS(self):

        sys1 = StateSpace([[1., 2.], [3., 4.]],
                [[5., 6.], [6., 8.]],
                [[9., 10.], [11., 12.]],
                [[13., 14.], [15., 16.]], 1)

        sys1_11 = sys1[0,1]
        np.testing.assert_array_almost_equal(sys1_11.A,
                sys1.A)
        np.testing.assert_array_almost_equal(sys1_11.B,
                sys1.B[:,1])
        np.testing.assert_array_almost_equal(sys1_11.C,
                sys1.C[0,:])
        np.testing.assert_array_almost_equal(sys1_11.D,
                sys1.D[0,1])

        assert sys1.dt == sys1_11.dt

    def test_dcgain_cont(self):
        """Test DC gain for continuous-time state-space systems"""
        sys = StateSpace(-2.,6.,5.,0)
        np.testing.assert_equal(sys.dcgain(), 15.)

        sys2 = StateSpace(-2, [6., 4.], [[5.],[7.],[11]], np.zeros((3,2)))
        expected = np.array([[15., 10.], [21., 14.], [33., 22.]])
        np.testing.assert_array_equal(sys2.dcgain(), expected)

        sys3 = StateSpace(0., 1., 1., 0.)
        np.testing.assert_equal(sys3.dcgain(), np.nan)

    def test_dcgain_discr(self):
        """Test DC gain for discrete-time state-space systems"""
        # static gain
        sys = StateSpace([], [], [], 2, True)
        np.testing.assert_equal(sys.dcgain(), 2)

        # averaging filter
        sys = StateSpace(0.5, 0.5, 1, 0, True)
        np.testing.assert_almost_equal(sys.dcgain(), 1)

        # differencer
        sys = StateSpace(0, 1, -1, 1, True)
        np.testing.assert_equal(sys.dcgain(), 0)

        # summer
        sys = StateSpace(1, 1, 1, 0, True)
        np.testing.assert_equal(sys.dcgain(), np.nan)

    def test_dcgain_integrator(self):
        """DC gain when eigenvalue at DC returns appropriately sized array of nan"""
        # the SISO case is also tested in test_dc_gain_{cont,discr}
        import itertools
        # iterate over input and output sizes, and continuous (dt=None) and discrete (dt=True) time
        for inputs,outputs,dt in itertools.product(range(1,6),range(1,6),[None,True]):
            states = max(inputs,outputs)

            # a matrix that is singular at DC, and has no "useless" states as in _remove_useless_states
            a = np.triu(np.tile(2,(states,states)))
            # eigenvalues all +2, except for ...
            a[0,0] = 0 if dt is None else 1
            b = np.eye(max(inputs,states))[:states,:inputs]
            c = np.eye(max(outputs,states))[:outputs,:states]
            d = np.zeros((outputs,inputs))
            sys = StateSpace(a,b,c,d,dt)
            dc = np.squeeze(np.tile(np.nan,(outputs,inputs)))
            np.testing.assert_array_equal(dc, sys.dcgain())


    def test_scalarStaticGain(self):
        """Regression: can we create a scalar static gain?"""
        g1=StateSpace([],[],[],[2])
        g2=StateSpace([],[],[],[3])

        # make sure StateSpace internals, specifically ABC matrix
        # sizes, are OK for LTI operations
        g3 = g1*g2
        self.assertEqual(6, g3.D[0,0])
        g4 = g1+g2
        self.assertEqual(5, g4.D[0,0])
        g5 = g1.feedback(g2)
        self.assertAlmostEqual(2./7, g5.D[0,0])
        g6 = g1.append(g2)
        np.testing.assert_array_equal(np.diag([2,3]),g6.D)

    def test_matrixStaticGain(self):
        """Regression: can we create matrix static gains?"""
        d1 = np.matrix([[1,2,3],[4,5,6]])
        d2 = np.matrix([[7,8],[9,10],[11,12]])
        g1=StateSpace([],[],[],d1)

        # _remove_useless_states was making A = [[0]]
        self.assertEqual((0,0), g1.A.shape)

        g2=StateSpace([],[],[],d2)
        g3=StateSpace([],[],[],d2.T)

        h1 = g1*g2
        np.testing.assert_array_equal(d1*d2, h1.D)
        h2 = g1+g3
        np.testing.assert_array_equal(d1+d2.T, h2.D)
        h3 = g1.feedback(g2)
        np.testing.assert_array_almost_equal(solve(np.eye(2)+d1*d2,d1), h3.D)
        h4 = g1.append(g2)
        np.testing.assert_array_equal(block_diag(d1,d2),h4.D)


    def test_remove_useless_states(self):
        """Regression: _remove_useless_states gives correct ABC sizes"""
        g1 = StateSpace(np.zeros((3,3)),
                        np.zeros((3,4)),
                        np.zeros((5,3)),
                        np.zeros((5,4)))
        self.assertEqual((0,0), g1.A.shape)
        self.assertEqual((0,4), g1.B.shape)
        self.assertEqual((5,0), g1.C.shape)
        self.assertEqual((5,4), g1.D.shape)
        self.assertEqual(0, g1.states)


    def test_BadEmptyMatrices(self):
        """Mismatched ABCD matrices when some are empty"""
        self.assertRaises(ValueError,StateSpace, [1], [],  [],  [1])
        self.assertRaises(ValueError,StateSpace, [1], [1], [],  [1])
        self.assertRaises(ValueError,StateSpace, [1], [],  [1], [1])
        self.assertRaises(ValueError,StateSpace, [],  [1], [],  [1])
        self.assertRaises(ValueError,StateSpace, [],  [1], [1], [1])
        self.assertRaises(ValueError,StateSpace, [],  [],  [1], [1])
        self.assertRaises(ValueError,StateSpace, [1], [1], [1], [])


    def test_minrealStaticGain(self):
        """Regression: minreal on static gain was failing"""
        g1 = StateSpace([],[],[],[1])
        g2 = g1.minreal()
        np.testing.assert_array_equal(g1.A, g2.A)
        np.testing.assert_array_equal(g1.B, g2.B)
        np.testing.assert_array_equal(g1.C, g2.C)
        np.testing.assert_array_equal(g1.D, g2.D)


class TestRss(unittest.TestCase):
    """These are tests for the proper functionality of statesp.rss."""

    def setUp(self):
        # Number of times to run each of the randomized tests.
        self.numTests = 100
        # Maxmimum number of states to test + 1
        self.maxStates = 10
        # Maximum number of inputs and outputs to test + 1
        self.maxIO = 5

    def testShape(self):
        """Test that rss outputs have the right state, input, and output
        size."""

        for states in range(1, self.maxStates):
            for inputs in range(1, self.maxIO):
                for outputs in range(1, self.maxIO):
                    sys = matlab.rss(states, outputs, inputs)
                    self.assertEqual(sys.states, states)
                    self.assertEqual(sys.inputs, inputs)
                    self.assertEqual(sys.outputs, outputs)

    def testPole(self):
        """Test that the poles of rss outputs have a negative real part."""

        for states in range(1, self.maxStates):
            for inputs in range(1, self.maxIO):
                for outputs in range(1, self.maxIO):
                    sys = matlab.rss(states, outputs, inputs)
                    p = sys.pole()
                    for z in p:
                        self.assertTrue(z.real < 0)

class TestDrss(unittest.TestCase):
    """These are tests for the proper functionality of statesp.drss."""

    def setUp(self):
        # Number of times to run each of the randomized tests.
        self.numTests = 100
        # Maxmimum number of states to test + 1
        self.maxStates = 10
        # Maximum number of inputs and outputs to test + 1
        self.maxIO = 5

    def testShape(self):
        """Test that drss outputs have the right state, input, and output
        size."""

        for states in range(1, self.maxStates):
            for inputs in range(1, self.maxIO):
                for outputs in range(1, self.maxIO):
                    sys = matlab.drss(states, outputs, inputs)
                    self.assertEqual(sys.states, states)
                    self.assertEqual(sys.inputs, inputs)
                    self.assertEqual(sys.outputs, outputs)

    def testPole(self):
        """Test that the poles of drss outputs have less than unit magnitude."""

        for states in range(1, self.maxStates):
            for inputs in range(1, self.maxIO):
                for outputs in range(1, self.maxIO):
                    sys = matlab.drss(states, outputs, inputs)
                    p = sys.pole()
                    for z in p:
                        self.assertTrue(abs(z) < 1)


    def testPoleStatic(self):
        """Regression: pole() of static gain is empty array"""
        np.testing.assert_array_equal(np.array([]),
                                      StateSpace([],[],[],[[1]]).pole())


def suite():
   return unittest.TestLoader().loadTestsFromTestCase(TestStateSpace)


if __name__ == "__main__":
    unittest.main()
