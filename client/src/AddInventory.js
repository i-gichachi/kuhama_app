import React, { useContext } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { UserContext } from './UserContext'; 

const InventorySchema = Yup.object().shape({
    item_name: Yup.string().required('Item Name is required'),
    quantity: Yup.number().min(1, 'Quantity must be at least 1').required('Quantity is required'),
    description: Yup.string().required('Description is required'),
    category: Yup.string().required('Category is required'),
    condition: Yup.string().required('Condition is required')
});

const AddInventory = () => {
    const { user } = useContext(UserContext);

    const handleSubmit = async (values, { setSubmitting, resetForm }) => {
        if (user && user.user_type === 'customer') {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch('/inventory/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(values),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                alert('Item added to inventory successfully');
                resetForm();
            } catch (error) {
                console.error('Error adding inventory item:', error);
                alert('Failed to add inventory item');
            }
        } else {
            alert('Access denied. Only customers can add inventory items.');
        }
        setSubmitting(false);
    };

    return (
        <div>
            <h1>Add Inventory Item</h1>
            <Formik
                initialValues={{
                    item_name: '',
                    quantity: 1,
                    description: '',
                    category: '',
                    condition: ''
                }}
                validationSchema={InventorySchema}
                onSubmit={handleSubmit}
            >
                {({ isSubmitting }) => (
                    <Form>
                        <div>
                            <label htmlFor="item_name">Item Name</label>
                            <Field name="item_name" type="text" />
                            <ErrorMessage name="item_name" component="div" />
                        </div>

                        <div>
                            <label htmlFor="quantity">Quantity</label>
                            <Field name="quantity" type="number" />
                            <ErrorMessage name="quantity" component="div" />
                        </div>

                        <div>
                            <label htmlFor="description">Description</label>
                            <Field name="description" type="text" />
                            <ErrorMessage name="description" component="div" />
                        </div>

                        <div>
                            <label htmlFor="category">Category</label>
                            <Field name="category" type="text" />
                            <ErrorMessage name="category" component="div" />
                        </div>

                        <div>
                            <label htmlFor="condition">Condition</label>
                            <Field name="condition" type="text" />
                            <ErrorMessage name="condition" component="div" />
                        </div>

                        <button type="submit" disabled={isSubmitting}>
                            Add Item
                        </button>
                    </Form>
                )}
            </Formik>
        </div>
    );
};

export default AddInventory;
