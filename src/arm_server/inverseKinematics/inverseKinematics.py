import numpy as np

class arm4DOF_kinematics:
    def __init__(self, arm_specs: list):
        self.l1 = arm_specs[0]
        self.l2 = arm_specs[1]
        self.l3 = arm_specs[2]

    def compute_FK(self, angle_coords):
        theta_base, theta_1, theta_2, theta_3 = angle_coords
        u = (self.l1 * np.cos(theta_1)
             + self.l2 * np.cos(theta_1 + theta_2)
             + self.l3 * np.cos(theta_1 + theta_2 + theta_3))
        z = (self.l1 * np.sin(theta_1)
             + self.l2 * np.sin(theta_1 + theta_2)
             + self.l3 * np.sin(theta_1 + theta_2 + theta_3))
        return u * np.sin(theta_base), u * np.cos(theta_base), z

    def compute_IK(
        self,
        cartesian_coords: list,
        initial_angles=None,
        joint_limits=None,
        tolerance=1e-6,
        phi_samples=1440,
        min_height=0.0,
    ):
        x, y, z = np.asarray(cartesian_coords, dtype=float)
        if z < min_height - tolerance:
            raise ValueError("target is below the ground")

        if joint_limits is None:
            joint_limits = [(-np.pi, np.pi)] * 4
        lower = np.array([l[0] for l in joint_limits], dtype=float)
        upper = np.array([l[1] for l in joint_limits], dtype=float)
        if np.any(lower >= upper):
            raise ValueError("invalid joint limits")

        ref = np.zeros(4) if initial_angles is None else np.asarray(initial_angles, float)

        r = np.hypot(x, y)
        base = np.arctan2(x, y)
        base_options = [(base, r), (self._wrap(base + np.pi), -r)]

        best, best_cost = None, np.inf
        for b, u in base_options:
            b = self._fit(b, lower[0], upper[0])
            if b is None:
                continue
            cand = self._planar_candidates(u, z, phi_samples)
            if cand is None:
                continue
            fitted = np.stack(
                [self._fit_array(cand[:, i], lower[i + 1], upper[i + 1]) for i in range(3)],
                axis=1,
            )
            ok = np.all(np.isfinite(fitted), axis=1)
            t1, t2, t3 = fitted[:, 0], fitted[:, 1], fitted[:, 2]
            h_elbow = self.l1 * np.sin(t1)
            h_wrist = h_elbow + self.l2 * np.sin(t1 + t2)
            h_tip = h_wrist + self.l3 * np.sin(t1 + t2 + t3)
            ok &= (h_elbow >= min_height - tolerance)
            ok &= (h_wrist >= min_height - tolerance)
            ok &= (h_tip >= min_height - tolerance)
            if not np.any(ok):
                continue
            fitted = fitted[ok]
            diff = self._wrap(fitted - ref[1:])
            cost = np.sum(diff ** 2, axis=1) + self._wrap(b - ref[0]) ** 2
            i = np.argmin(cost)
            if cost[i] < best_cost:
                best_cost = cost[i]
                best = np.array([b, *fitted[i]])

        if best is None:
            raise ValueError("no ground-safe, in-limit solution exists for this target")
        return best

    def _planar_candidates(self, u, z, n):
        phi = np.linspace(-np.pi, np.pi, n, endpoint=False)
        wu = u - self.l3 * np.cos(phi)
        wz = z - self.l3 * np.sin(phi)
        d2 = wu ** 2 + wz ** 2
        c2 = (d2 - self.l1 ** 2 - self.l2 ** 2) / (2 * self.l1 * self.l2)
        reach = np.abs(c2) <= 1 + 1e-9
        if not np.any(reach):
            return None
        phi, wu, wz, c2 = phi[reach], wu[reach], wz[reach], np.clip(c2[reach], -1, 1)
        out = []
        for sign in (+1.0, -1.0):
            t2 = sign * np.arccos(c2)
            t1 = np.arctan2(wz, wu) - np.arctan2(self.l2 * np.sin(t2), self.l1 + self.l2 * np.cos(t2))
            t3 = phi - t1 - t2
            out.append(np.stack([self._wrap(t1), self._wrap(t2), self._wrap(t3)], axis=1))
        return np.concatenate(out, axis=0)

    @staticmethod
    def _wrap(a):
        return np.arctan2(np.sin(a), np.cos(a))

    @staticmethod
    def _fit(a, lo, hi):
        for k in (-1, 0, 1):
            v = a + 2 * np.pi * k
            if lo - 1e-12 <= v <= hi + 1e-12:
                return v
        return None

    @staticmethod
    def _fit_array(a, lo, hi):
        res = np.full_like(a, np.nan)
        for k in (-1, 0, 1):
            v = a + 2 * np.pi * k
            m = np.isnan(res) & (v >= lo - 1e-12) & (v <= hi + 1e-12)
            res[m] = v[m]
        return res