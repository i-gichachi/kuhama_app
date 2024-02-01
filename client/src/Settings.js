import React, { useContext, useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { UserContext } from './UserContext'; 

const SettingsSchema = Yup.object().shape({
    first_name: Yup.string().required('First Name is required'),
    second_name: Yup.string(),
    surname: Yup.string().required('Surname is required'),
    username: Yup.string().required('Username is required'),
    email: Yup.string().email('Invalid email format').required('Email is required'),
    phone_number: Yup.string().matches(/^\d{9}$/, 'Phone number must be exactly 9 digits').required('Phone number is required'),
    gender: Yup.string().required('Gender is required'),
    location: Yup.string(),
    date_of_birth: Yup.date().required('Date of Birth is required'),
});

const Settings = () => {
    const { user, setUser } = useContext(UserContext);
    const [isEditing, setIsEditing] = useState(false);

    const counties = [
        "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo Marakwet", "Embu", "Garissa",
        "Homa Bay", "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi",
        "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu", "Machakos",
        "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa", "Murang'a",
        "Nairobi City", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua", "Nyeri",
        "Samburu", "Siaya", "Taita Taveta", "Tana River", "Tharaka Nithi", "Trans Nzoia",
        "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
    ];    

    const handleSubmit = async (values, { setSubmitting }) => {
        try {
            const response = await fetch('/user/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(values),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            alert('User information updated successfully');
            setIsEditing(false);
            setUser(values);
        } catch (error) {
            console.error('Error updating user info:', error);
        }
        setSubmitting(false);
    };

    if (!user) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Settings</h1>
            <Formik
                initialValues={user}
                validationSchema={SettingsSchema}
                onSubmit={handleSubmit}
                enableReinitialize
            >
                {({ isSubmitting }) => (
                    <Form>
                        <div>
                            <label htmlFor="first_name">First Name</label>
                            <Field name="first_name" type="text" disabled={!isEditing} />
                            <ErrorMessage name="first_name" component="div" />
                        </div>

                        <div>
                            <label htmlFor="second_name">Second Name</label>
                            <Field name="second_name" type="text" disabled={!isEditing} />
                            <ErrorMessage name="second_name" component="div" />
                        </div>

                        <div>
                            <label htmlFor="surname">Surname</label>
                            <Field name="surname" type="text" disabled={!isEditing} />
                            <ErrorMessage name="surname" component="div" />
                        </div>

                        <div>
                            <label htmlFor="username">Username</label>
                            <Field name="username" type="text" disabled={!isEditing} />
                            <ErrorMessage name="username" component="div" />
                        </div>

                        <div>
                            <label htmlFor="email">Email</label>
                            <Field name="email" type="email" disabled={!isEditing} />
                            <ErrorMessage name="email" component="div" />
                        </div>

                        <div>
                            <label htmlFor="phone_number">Phone Number</label>
                            <Field name="phone_number" type="text" disabled={!isEditing} />
                            <ErrorMessage name="phone_number" component="div" />
                        </div>

                        <div>
                            <label htmlFor="gender">Gender</label>
                            <Field name="gender" as="select" disabled={!isEditing}>
                                <option value="">Select Gender</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                            </Field>
                            <ErrorMessage name="gender" component="div" />
                        </div>

                        <div>
                            <label htmlFor="location">Location</label>
                            <Field name="location" as="select" disabled={!isEditing}>
                                <option value="">Select County</option>
                                {counties.map(county => (
                                    <option key={county} value={county}>{county}</option>
                                ))}
                            </Field>
                            <ErrorMessage name="location" component="div" />
                        </div>

                        <div>
                            <label htmlFor="date_of_birth">Date of Birth</label>
                            <Field name="date_of_birth" type="date" disabled={!isEditing} />
                            <ErrorMessage name="date_of_birth" component="div" />
                        </div>

                        {isEditing ? (
                            <>
                                <button type="submit" disabled={isSubmitting}>Save</button>
                                <button type="button" onClick={() => setIsEditing(false)}>Cancel</button>
                            </>
                        ) : (
                            <button type="button" onClick={() => setIsEditing(true)}>Edit</button>
                        )}
                    </Form>
                )}
            </Formik>
        </div>
    );
};

export default Settings
