import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { FaUser, FaLock } from 'react-icons/fa';
import { useNavigate, Link } from 'react-router-dom';

const loginSchema = Yup.object().shape({
    login: Yup.string().required('Required'),
    password: Yup.string().required('Required'),
});

const Login = () => {
    const navigate = useNavigate();

    const handleSubmit = async (values, { setSubmitting, setErrors }) => {
        try {
            const response = await fetch('http://127.0.0.1:5555/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(values),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            await response.json();
            window.alert('You have successfully logged into the system');
            navigate('/'); // Redirect to the landing page
        } catch (error) {
            if (error.message === 'Network response was not ok') {
                setErrors({ server: 'Invalid username, email, phone number, or password' });
            } else {
                console.log('Error:', error.message);
            }
        }

        setSubmitting(false);
    };

    return (
        <div>
            <h1>Login</h1>
            <Formik
                initialValues={{ login: '', password: '' }}
                validationSchema={loginSchema}
                onSubmit={handleSubmit}
            >
                {({ isSubmitting, errors }) => (
                    <Form>
                        <div>
                            <FaUser />
                            <Field type="text" name="login" placeholder="Username/Email/Phone" />
                            <ErrorMessage name="login" component="div" />
                        </div>

                        <div>
                            <FaLock />
                            <Field type="password" name="password" placeholder="Password" />
                            <ErrorMessage name="password" component="div" />
                        </div>

                        {errors.server && <div>{errors.server}</div>}

                        <button type="submit" disabled={isSubmitting}>
                            Login
                        </button>
                    </Form>
                )}
            </Formik>
            <p>
                Don't have an account? <Link to="/signup">Sign Up</Link>
            </p>
        </div>
    );
};

export default Login;
