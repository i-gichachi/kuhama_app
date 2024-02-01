import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useNavigate } from 'react-router-dom';

const SignupSchema = Yup.object().shape({
    first_name: Yup.string().required('Required'),
    second_name: Yup.string(),
    surname: Yup.string().required('Required'),
    username: Yup.string().required('Required'),
    email: Yup.string().email('Invalid email').required('Required'),
    phone_number: Yup.string().matches(/^\d{9}$/, 'Phone number must be exactly 9 digits').required('Required'),
    gender: Yup.string().oneOf(['male', 'female'], 'Invalid gender').required('Required'),
    date_of_birth: Yup.date().required('Required').max(new Date(), 'You must be at least 18 years old to register.'),
    password: Yup.string().matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$/, 'Password should have at least one lowercase, one uppercase, one number, and one special character').required('Required'),
    confirm_password: Yup.string().oneOf([Yup.ref('password'), null], 'Passwords must match').required('Required'),
    accept_terms: Yup.bool().oneOf([true], 'You must accept the terms and conditions').required('Required')
});

const Signup = () => {
    const navigate = useNavigate();

    const handleSubmit = async (values, { setSubmitting, setErrors }) => {
        try {
            const response = await fetch('http://127.0.0.1:5555/signup', {
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
            alert('User registered successfully');
            navigate('/login'); // Redirect to login after successful signup
        } catch (error) {
            console.log('Error:', error.message);
            setErrors({ server: error.message });
        }

        setSubmitting(false);
    };

    return (
        <div>
            <h1>Sign Up</h1>
            <Formik
                initialValues={{
                    first_name: '',
                    second_name: '',
                    surname: '',
                    username: '',
                    email: '',
                    phone_number: '',
                    gender: '',
                    date_of_birth: '',
                    password: '',
                    confirm_password: '',
                    accept_terms: false,
                }}
                validationSchema={SignupSchema}
                onSubmit={handleSubmit}
            >
                {({ isSubmitting, errors }) => (
                    <Form>
                        <label htmlFor="first_name">First Name</label>
                        <Field name="first_name" placeholder="First Name" />
                        <ErrorMessage name="first_name" component="div" />

                        <label htmlFor="second_name">Second Name</label>
                        <Field name="second_name" placeholder="Second Name" />
                        <ErrorMessage name="second_name" component="div" />

                        <label htmlFor="surname">Surname</label>
                        <Field name="surname" placeholder="Surname" />
                        <ErrorMessage name="surname" component="div" />

                        <label htmlFor="username">Username</label>
                        <Field name="username" placeholder="Username" />
                        <ErrorMessage name="username" component="div" />

                        <label htmlFor="email">Email</label>
                        <Field name="email" placeholder="Email" type="email" />
                        <ErrorMessage name="email" component="div" />

                        <label htmlFor="phone_number">Phone Number (+254)</label>
                        <Field name="phone_number" placeholder="712345678" />
                        <ErrorMessage name="phone_number" component="div" />

                        <label htmlFor="gender">Gender</label>
                        <Field name="gender" as="select">
                            <option value="">Select Gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                        </Field>
                        <ErrorMessage name="gender" component="div" />

                        <label htmlFor="date_of_birth">Date of Birth</label>
                        <Field name="date_of_birth" type="date" />
                        <ErrorMessage name="date_of_birth" component="div" />

                        <label htmlFor="password">Password</label>
                        <Field name="password" placeholder="Password" type="password" />
                        <ErrorMessage name="password" component="div" />

                        <label htmlFor="confirm_password">Confirm Password</label>
                        <Field name="confirm_password" placeholder="Confirm Password" type="password" />
                        <ErrorMessage name="confirm_password" component="div" />

                        <label htmlFor="accept_terms">
                            <Field type="checkbox" name="accept_terms" />
                            I accept the Terms and Conditions
                        </label>
                        <ErrorMessage name="accept_terms" component="div" />

                        {errors.server && <div>{errors.server}</div>}

                        <button type="submit" disabled={isSubmitting}>
                            Sign Up
                        </button>
                    </Form>
                )}
            </Formik>
        </div>
    );
};

export default Signup;
