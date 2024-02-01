import React, { useContext, useState, useEffect } from 'react';
import { UserContext } from './UserContext';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

const InventorySchema = Yup.object().shape({
    item_name: Yup.string().required('Item Name is required'),
    quantity: Yup.number().min(1, 'Quantity must be at least 1').required('Quantity is required'),
    description: Yup.string().required('Description is required'),
    category: Yup.string().required('Category is required'),
    condition: Yup.string().required('Condition is required')
});

const InventoryManagement = () => {
    const { user } = useContext(UserContext);
    const [inventory, setInventory] = useState([]);
    const [editingItem, setEditingItem] = useState(null);
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        const fetchInventory = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch('/inventory', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch inventory');
                }

                const data = await response.json();
                setInventory(data);
            } catch (error) {
                console.error('Error fetching inventory:', error);
            }
        };

        if (user && user.user_type === 'customer') {
            fetchInventory();
        }
    }, [user]);

    const handleEdit = (item) => {
        setEditingItem(item);
        setIsEditing(true);
    };

    const handleDelete = async (itemId) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/inventory/delete/${itemId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to delete inventory item');
            }

            alert('Inventory item deleted successfully');
            setInventory(inventory.filter(item => item.id !== itemId));
        } catch (error) {
            console.error('Error deleting inventory item:', error);
        }
    };

    const handleSubmit = async (values, { setSubmitting }) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/inventory/update/${editingItem.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(values)
            });

            if (!response.ok) {
                throw new Error('Failed to update inventory item');
            }

            alert('Inventory item updated successfully');
            setInventory(inventory.map(item => item.id === editingItem.id ? values : item));
            setIsEditing(false);
            setEditingItem(null);
        } catch (error) {
            console.error('Error updating inventory item:', error);
        }
        setSubmitting(false);
    };

    if (!user || user.user_type !== 'customer') {
        return <div>Access Denied</div>;
    }

    return (
        <div>
            <h1>Inventory Management</h1>
            {isEditing && editingItem && (
                <Formik
                    initialValues={editingItem}
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

                            <button type="submit" disabled={isSubmitting}>Save</button>
                            <button type="button" onClick={() => setIsEditing(false)}>Cancel</button>
                            
                        </Form>
                    )}
                </Formik>
            )}
            {!isEditing && (
                <table>
                    <thead>
                        <tr>
                            <th>Item Name</th>
                            <th>Quantity</th>
                            <th>Description</th>
                            <th>Category</th>
                            <th>Condition</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {inventory.map(item => (
                            <tr key={item.id}>
                                <td>{item.item_name}</td>
                                <td>{item.quantity}</td>
                                <td>{item.description}</td>
                                <td>{item.category}</td>
                                <td>{item.condition}</td>
                                <td>
                                    <button onClick={() => handleEdit(item)}>Edit</button>
                                    <button onClick={() => handleDelete(item.id)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default InventoryManagement;
