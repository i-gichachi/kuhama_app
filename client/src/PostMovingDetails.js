import React, { useContext, useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { UserContext } from './UserContext';

const calculateDistance = (lat1, lon1, lat2, lon2) => {
    // Haversine distance calculation
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in km
};

const calculatePrice = (distance, homeSize, packingService) => {
    const basePricePerKm = 500; // 500 Ksh per km
    const sizeFactor = {
        "bedsitter": 1,
        "one bedroom": 1.5,
        "studio": 1.2,
        "two bedroom": 2
    };
    const packingServiceFee = packingService ? 3000 : 0; // 3000 Ksh for packing service

    return distance * basePricePerKm * sizeFactor[homeSize] + packingServiceFee;
};

const MovingDetailsSchema = Yup.object().shape({
    from_location: Yup.string().required('From location is required'),
    from_lat: Yup.number().required('From latitude is required'),
    from_lon: Yup.number().required('From longitude is required'),
    to_location: Yup.string().required('To location is required'),
    to_lat: Yup.number().required('To latitude is required'),
    to_lon: Yup.number().required('To longitude is required'),
    home_size: Yup.string().oneOf(['bedsitter', 'one bedroom', 'studio', 'two bedroom'], 'Invalid home size').required('Home size is required'),
    moving_date: Yup.date().min(addDays(new Date(), 7), 'Moving date should be at least 7 days from today').required('Moving date is required'),
    packing_service: Yup.boolean(),
    additional_details: Yup.string()
});

const PostMovingDetails = () => {
    const { user } = useContext(UserContext);
    const [price, setPrice] = useState(0);

    const handleSubmit = async (values, { setSubmitting, resetForm }) => {
        if (user && user.user_type === 'customer') {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch('/moving/add', { // Replace with your API endpoint
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        ...values,
                        price: calculatePrice(
                            calculateDistance(values.from_lat, values.from_lon, values.to_lat, values.to_lon), 
                            values.home_size, 
                            values.packing_service
                        )
                    }),
                });
    
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
    
                const data = await response.json();
                alert(data.message); // Display success message from the server
                resetForm(); // Reset the form after successful submission
            } catch (error) {
                console.error('Error posting moving details:', error);
                alert('Failed to post moving details'); // Display error message
            }
        } else {
            alert('Access denied. Only customers can post moving details.');
        }
        setSubmitting(false);
    };
        
    return (
        <div>
            <h1>Post Moving Details</h1>
            <Formik
                initialValues={{
                    from_location: '',
                    from_lat: '',
                    from_lon: '',
                    to_location: '',
                    to_lat: '',
                    to_lon: '',
                    home_size: '',
                    moving_date: '',
                    packing_service: false,
                    additional_details: ''
                }}
                validationSchema={MovingDetailsSchema}
                onSubmit={handleSubmit}
            >
                {({ values, setFieldValue, isSubmitting }) => (
                    <Form>
                        {/* From Location Fields */}
                        <div>
                            <label htmlFor="from_location">From Location</label>
                            <Field name="from_location" type="text" />
                            <ErrorMessage name="from_location" component="div" />
                        </div>
                        <div>
                            <label htmlFor="from_lat">From Latitude</label>
                            <Field name="from_lat" type="number" placeholder="e.g., -1.2921"
                                onChange={(e) => {
                                    setFieldValue('from_lat', e.target.value);
                                    setPrice(calculatePrice(calculateDistance(values.from_lat, values.from_lon, values.to_lat, values.to_lon), values.home_size, values.packing_service));
                                }}
                            />
                            <ErrorMessage name="from_lat" component="div" />
                        </div>
                        <div>
                            <label htmlFor="from_lon">From Longitude</label>
                            <Field name="from_lon" type="number" placeholder="e.g., 36.8219"
                                onChange={(e) => {
                                    setFieldValue('from_lon', e.target.value);
                                    setPrice(calculatePrice(calculateDistance(values.from_lat, values.from_lon, values.to_lat, values.to_lon), values.home_size, values.packing_service));
                                }}
                            />
                            <ErrorMessage name="from_lon" component="div" />
                        </div>

                        {/* To Location Fields */}
                        <div>
                            <label htmlFor="to_location">To Location</label>
                            <Field name="to_location" type="text" />
                            <ErrorMessage name="to_location" component="div" />
                        </div>
                        <div>
                            <label htmlFor="to_lat">To Latitude</label>
                            <Field name="to_lat" type="number" placeholder="e.g., -1.2921"
                                onChange={(e) => {
                                    setFieldValue('to_lat', e.target.value);
                                    setPrice(calculatePrice(calculateDistance(values.from_lat, values.from_lon, values.to_lat, values.to_lon), values.home_size, values.packing_service));
                                }}
                            />
                            <ErrorMessage name="to_lat" component="div" />
                        </div>
                        <div>
                            <label htmlFor="to_lon">To Longitude</label>
                            <Field name="to_lon" type="number" placeholder="e.g., 36.8219"
                                onChange={(e) => {
                                    setFieldValue('to_lon', e.target.value);
                                    setPrice(calculatePrice(calculateDistance(values.from_lat, values.from_lon, values.to_lat, values.to_lon), values.home_size, values.packing_service));
                                }}
                            />
                            <ErrorMessage name="to_lon" component="div" />
                        </div>

                        {/* Other Fields */}
                        <div>
                            <label htmlFor="home_size">Home Size</label>
                            <Field name="home_size" as="select" 
                                onChange={(e) => {
                                    setFieldValue('home_size', e.target.value);
                                    setPrice(calculatePrice(calculateDistance(values.from_lat, values.from_lon, values.to_lat, values.to_lon), e.target.value, values.packing_service));
                                }}
                            >
                                <option value="">Select Home Size</option>
                                <option value="bedsitter">Bedsitter</option>
                                <option value="one bedroom">One Bedroom</option>
                                <option value="studio">Studio</option>
                                <option value="two bedroom">Two Bedroom</option>
                            </Field>
                            <ErrorMessage name="home_size" component="div" />
                        </div>

                        <div>
                            <label htmlFor="moving_date">Moving Date</label>
                            <Field name="moving_date" type="date" />
                            <ErrorMessage name="moving_date" component="div" />
                        </div>

                        <div>
                            <label htmlFor="packing_service">Packing Service</label>
                            <Field name="packing_service" type="checkbox"
                                onChange={(e) => {
                                    setFieldValue('packing_service', e.target.checked);
                                    setPrice(calculatePrice(calculateDistance(values.from_lat, values.from_lon, values.to_lat, values.to_lon), values.home_size, e.target.checked));
                                }}
                            />
                        </div>

                        <div>
                            <label htmlFor="additional_details">Additional Details</label>
                            <Field name="additional_details" type="text" />
                            <ErrorMessage name="additional_details" component="div" />
                        </div>

                        <p>Estimated Price: Ksh {price.toFixed(2)}</p>

                        <button type="submit" disabled={isSubmitting}>Submit Moving Details</button>
                    </Form>
                )}
            </Formik>
        </div>
    );
};

export default PostMovingDetails;